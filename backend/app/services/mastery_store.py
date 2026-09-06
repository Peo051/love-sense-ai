from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import SkillModel
from app.models.student_skill_mastery import StudentSkillMastery
from app.schemas.mastery_schema import SkillMasteryResponse, StudentMasterySummaryResponse
from app.tutor.mastery import DeterministicMasteryModel, MasteryEvent
from app.tutor.skill_taxonomy import CSHARP_OOP_SKILLS_V1, SkillTaxonomy


class MasteryRepository:
    """
    Repository quản lý dữ liệu mức độ thuần thục kỹ năng của sinh viên (Student Skill Mastery).
    """

    @classmethod
    async def get_user_mastery(
        cls,
        db: AsyncSession,
        user_id: str,
        skill_id: str,
    ) -> Optional[StudentSkillMastery]:
        """Lấy bản ghi mastery của sinh viên cho một kỹ năng cụ thể."""
        canonical_code = SkillTaxonomy.map_knowledge_component(skill_id) or skill_id
        stmt = select(StudentSkillMastery).where(
            StudentSkillMastery.user_id == user_id,
            StudentSkillMastery.skill_id == canonical_code,
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def get_or_create_mastery(
        cls,
        db: AsyncSession,
        user_id: str,
        skill_id: str,
    ) -> StudentSkillMastery:
        """
        Lấy bản ghi mastery hiện có, hoặc khởi tạo bản ghi mới với giá trị trung tính:
        mastery_score = 0.5, counters = 0, last_practiced_at = None.
        """
        canonical_code = SkillTaxonomy.map_knowledge_component(skill_id) or skill_id
        record = await cls.get_user_mastery(db, user_id, canonical_code)
        if record:
            return record

        record = StudentSkillMastery(
            user_id=user_id,
            skill_id=canonical_code,
            mastery_score=DeterministicMasteryModel.INITIAL_MASTERY,
            success_count=0,
            failure_count=0,
            hint_count=0,
            last_practiced_at=None,
        )
        db.add(record)
        await db.flush()
        return record

    @classmethod
    async def list_user_masteries(
        cls,
        db: AsyncSession,
        user_id: str,
    ) -> list[StudentSkillMastery]:
        """Liệt kê tất cả các bản ghi mastery đã được lưu của sinh viên."""
        stmt = (
            select(StudentSkillMastery)
            .where(StudentSkillMastery.user_id == user_id)
            .order_by(StudentSkillMastery.skill_id)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def record_practice_attempt(
        cls,
        db: AsyncSession,
        user_id: str,
        skill_ids: list[str],
        event: MasteryEvent,
        hints_used: int = 0,
        practice_time: Optional[datetime] = None,
    ) -> list[StudentSkillMastery]:
        """
        Ghi nhận kết quả luyện tập của sinh viên và cập nhật điểm tất định cho tất cả các kỹ năng liên quan.
        """
        if not skill_ids:
            return []

        # Chuẩn hóa danh sách kỹ năng qua taxonomy
        canonical_skills = SkillTaxonomy.map_knowledge_components(skill_ids)
        if not canonical_skills:
            # Nếu toàn bộ kỹ năng không nhận diện được, fallback kỹ năng class_object
            canonical_skills = ["csharp.class_object"]

        timestamp = practice_time or datetime.now(timezone.utc)
        updated_records: list[StudentSkillMastery] = []

        for code in canonical_skills:
            record = await cls.get_or_create_mastery(db, user_id, code)
            new_state = DeterministicMasteryModel.apply_event_to_state(
                current_score=record.mastery_score,
                success_count=record.success_count,
                failure_count=record.failure_count,
                hint_count=record.hint_count,
                event=event,
                hints_used_in_attempt=hints_used,
                practice_time=timestamp,
            )

            record.mastery_score = new_state["mastery_score"]
            record.success_count = new_state["success_count"]
            record.failure_count = new_state["failure_count"]
            record.hint_count = new_state["hint_count"]
            record.last_practiced_at = new_state["last_practiced_at"]
            updated_records.append(record)

        await db.commit()
        for r in updated_records:
            await db.refresh(r)

        return updated_records

    @classmethod
    async def get_user_mastery_summary(
        cls,
        db: AsyncSession,
        user_id: str,
    ) -> StudentMasterySummaryResponse:
        """
        Tổng hợp toàn diện trạng thái thuần thục của sinh viên đối với toàn bộ taxonomy C# OOP V1:
        Kỹ năng nào chưa làm bài sẽ hiển thị ở mức trung tính (0.5).
        """
        all_canonical_skills = SkillTaxonomy.list_skills(taxonomy_version="v1")
        existing_records = {r.skill_id: r for r in await cls.list_user_masteries(db, user_id)}

        skill_responses: list[SkillMasteryResponse] = []
        total_score = 0.0

        for skill in all_canonical_skills:
            rec = existing_records.get(skill.code)
            if rec:
                score = rec.mastery_score
                succ = rec.success_count
                fail = rec.failure_count
                hints = rec.hint_count
                last_p = rec.last_practiced_at
                c_at = rec.created_at
                u_at = rec.updated_at
            else:
                score = DeterministicMasteryModel.INITIAL_MASTERY
                succ = 0
                fail = 0
                hints = 0
                last_p = None
                c_at = None
                u_at = None

            total_score += score
            skill_responses.append(
                SkillMasteryResponse(
                    skill_id=skill.code,
                    skill_name=skill.name,
                    mastery_score=score,
                    success_count=succ,
                    failure_count=fail,
                    hint_count=hints,
                    last_practiced_at=last_p,
                    created_at=c_at,
                    updated_at=u_at,
                )
            )

        total_skills = len(all_canonical_skills)
        practiced_skills = len(existing_records)
        avg_score = round(total_score / total_skills, 4) if total_skills > 0 else 0.5

        return StudentMasterySummaryResponse(
            total_skills=total_skills,
            practiced_skills=practiced_skills,
            average_mastery=avg_score,
            skills=skill_responses,
        )
