from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import SkillModel
from app.models.student_skill_mastery import StudentSkillMastery
from app.schemas.mastery_schema import (
    RecentAttemptSummary,
    SkillMasteryResponse,
    StudentMasterySummaryResponse,
    StudentProgressDashboardResponse,
)
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

    @classmethod
    async def get_student_progress_dashboard(
        cls,
        db: AsyncSession,
        user_id: str,
    ) -> StudentProgressDashboardResponse:
        """
        Tổng hợp toàn diện dữ liệu bảng theo dõi tiến độ học tập của sinh viên (APT-023).
        Đảm bảo strict user ownership và không dùng giá trị hardcoded.
        """
        # 1. Lấy thông tin mastery theo toàn bộ taxonomy
        mastery_summary = await cls.get_user_mastery_summary(db, user_id)
        all_skills = mastery_summary.skills

        # 2. Phân loại kỹ năng đã thực hành, vững vàng, và cần ôn luyện
        practiced_skill_list = [
            s for s in all_skills
            if (s.success_count + s.failure_count) > 0 or s.last_practiced_at is not None
        ]
        practiced_skills_count = len(practiced_skill_list)

        # Điểm ước lượng thuần thục hiện tại: trung bình trên các kỹ năng đã thực hành (nếu chưa có thì 0.5 trung tính)
        if practiced_skills_count > 0:
            current_mastery_estimate = round(
                sum(s.mastery_score for s in practiced_skill_list) / practiced_skills_count, 4
            )
        else:
            current_mastery_estimate = DeterministicMasteryModel.INITIAL_MASTERY

        # Kỹ năng vững vàng (Strong topics): mastery >= 0.65 và có ít nhất 1 lần thành công
        strong_topics = sorted(
            [s for s in practiced_skill_list if s.mastery_score >= 0.65 and s.success_count > 0],
            key=lambda s: (s.mastery_score, s.success_count),
            reverse=True,
        )

        # Kỹ năng cần luyện tập thêm (Topics needing practice):
        needing_practice = [
            s for s in practiced_skill_list
            if s.failure_count > 0 or s.mastery_score < 0.55
        ]
        needing_practice.sort(key=lambda s: (s.mastery_score, -s.failure_count))

        # Nếu số kỹ năng cần ôn luyện ít hơn 3, gợi ý thêm các kỹ năng chưa làm bắt đầu từ kỹ năng nền tảng
        if len(needing_practice) < 3:
            unpracticed = [s for s in all_skills if s not in practiced_skill_list]
            for unp in unpracticed:
                if unp not in needing_practice:
                    needing_practice.append(unp)
                if len(needing_practice) >= 5:
                    break

        # 3. Lấy danh sách các lần thử gần nhất từ StudentAttempt join LearningSession
        from app.models.learning_session import LearningSession, StudentAttempt
        from app.models.mastery_audit import StudentMasteryAudit

        stmt_attempts = (
            select(StudentAttempt, LearningSession)
            .join(LearningSession, StudentAttempt.session_id == LearningSession.id)
            .where(LearningSession.user_id == user_id)
            .order_by(StudentAttempt.created_at.desc())
            .limit(10)
        )
        res_attempts = await db.execute(stmt_attempts)
        attempts_rows = res_attempts.all()

        recent_attempts: list[RecentAttemptSummary] = []
        for att, sess in attempts_rows:
            raw_kc = []
            if isinstance(att.diagnosis, dict):
                raw_kc = att.diagnosis.get("knowledge_components") or []
            mapped_skills = SkillTaxonomy.map_knowledge_components(raw_kc) if raw_kc else []
            if not mapped_skills and sess.topic:
                mapped_skills = [sess.topic]

            hints_used = 0
            highest_hint = 0
            if isinstance(att.hint_progression, dict):
                hints_used = int(att.hint_progression.get("hints_used") or 0)
                highest_hint = int(
                    att.hint_progression.get("highest_hint_level_used")
                    or att.hint_progression.get("highest_hint_level")
                    or 0
                )

            title = (att.problem_reference or sess.title or "Bài tập C# OOP").strip()
            if len(title) > 90:
                title = title[:87] + "..."

            recent_attempts.append(
                RecentAttemptSummary(
                    attempt_id=att.id,
                    session_id=sess.id,
                    problem_title=title,
                    outcome=att.success_state,
                    skills=mapped_skills,
                    hints_used=hints_used,
                    highest_hint_level=highest_hint,
                    created_at=att.created_at,
                )
            )

        # 4. Lấy audit records của user để tính toán các chỉ số
        stmt_audits = (
            select(StudentMasteryAudit)
            .where(StudentMasteryAudit.user_id == user_id)
            .order_by(StudentMasteryAudit.created_at.desc())
        )
        res_audits = await db.execute(stmt_audits)
        audits = list(res_audits.scalars().all())

        # Nếu không có attempts từ StudentAttempt nhưng có audits (ví dụ practice trực tiếp),
        # tạo recent attempts từ audits để hiển thị đầy đủ
        if not recent_attempts and audits:
            seen_attempt_ids = set()
            for a in audits:
                if a.attempt_id in seen_attempt_ids:
                    continue
                seen_attempt_ids.add(a.attempt_id)

                if a.event_type == MasteryEvent.INDEPENDENT_SUCCESS:
                    a_hints = 0
                    a_lvl = 0
                elif a.event_type == MasteryEvent.HINT_L1_SUCCESS:
                    a_hints = 1
                    a_lvl = 1
                elif a.event_type == MasteryEvent.HINT_L2_L3_SUCCESS:
                    a_hints = 2
                    a_lvl = 2
                elif a.event_type == MasteryEvent.EXPLICIT_SOLUTION_L4:
                    a_hints = 4
                    a_lvl = 4
                else:
                    a_hints = 0
                    a_lvl = 0

                skill_obj = SkillTaxonomy.get_skill(a.skill_id)
                skill_title = skill_obj.name if skill_obj else a.skill_id
                recent_attempts.append(
                    RecentAttemptSummary(
                        attempt_id=a.attempt_id,
                        session_id=None,
                        problem_title=f"Luyện tập kỹ năng: {skill_title}",
                        outcome="resolved" if "success" in a.event_type else a.event_type,
                        skills=[a.skill_id],
                        hints_used=a_hints,
                        highest_hint_level=a_lvl,
                        created_at=a.created_at,
                    )
                )
                if len(recent_attempts) >= 10:
                    break
        elif not recent_attempts and practiced_skill_list:
            # Fallback nếu thực hành qua direct practice API
            for s in practiced_skill_list:
                skill_obj = SkillTaxonomy.get_skill(s.skill_id)
                skill_title = skill_obj.name if skill_obj else s.skill_id
                outcome = "resolved" if s.success_count > 0 else "unresolved"
                lvl = min(4, s.hint_count) if s.hint_count > 0 else 0
                recent_attempts.append(
                    RecentAttemptSummary(
                        attempt_id=f"practice-{s.skill_id}",
                        session_id=None,
                        problem_title=f"Luyện tập kỹ năng: {skill_title}",
                        outcome=outcome,
                        skills=[s.skill_id],
                        hints_used=s.hint_count,
                        highest_hint_level=lvl,
                        created_at=s.last_practiced_at or datetime.now(timezone.utc),
                    )
                )
                if len(recent_attempts) >= 10:
                    break

        # 5. Tính toán các chỉ số: total_attempts, independent_solution_rate, average_hint_level
        audits_by_attempt: dict[str, list[StudentMasteryAudit]] = {}
        for a in audits:
            audits_by_attempt.setdefault(a.attempt_id, []).append(a)

        unique_attempt_ids = set(audits_by_attempt.keys())
        for att in recent_attempts:
            unique_attempt_ids.add(att.attempt_id)

        total_practice_events = sum(s.success_count + s.failure_count for s in practiced_skill_list)
        total_attempts_count = max(len(unique_attempt_ids), total_practice_events)

        successful_attempts_count = 0
        independent_success_count = 0
        hint_levels_recorded: list[int] = []

        for att_id, att_audits in audits_by_attempt.items():
            primary_event = att_audits[0].event_type
            if primary_event == MasteryEvent.INDEPENDENT_SUCCESS:
                independent_success_count += 1
                successful_attempts_count += 1
                hint_levels_recorded.append(0)
            elif primary_event == MasteryEvent.HINT_L1_SUCCESS:
                successful_attempts_count += 1
                hint_levels_recorded.append(1)
            elif primary_event == MasteryEvent.HINT_L2_L3_SUCCESS:
                successful_attempts_count += 1
                hint_levels_recorded.append(2)
            elif primary_event == MasteryEvent.EXPLICIT_SOLUTION_L4:
                successful_attempts_count += 1
                hint_levels_recorded.append(4)
            elif primary_event == MasteryEvent.UNRESOLVED_ATTEMPT:
                hint_levels_recorded.append(1)

        for ra in recent_attempts:
            if ra.attempt_id not in audits_by_attempt:
                norm_outcome = ra.outcome.lower()
                is_succ = norm_outcome in ("resolved", "likely_resolved", "completed")
                if is_succ:
                    successful_attempts_count += 1
                    if ra.hints_used == 0 and ra.highest_hint_level == 0:
                        independent_success_count += 1
                if ra.highest_hint_level >= 0 and not audits_by_attempt:
                    hint_levels_recorded.append(ra.highest_hint_level)

        if successful_attempts_count == 0 and not audits and practiced_skill_list:
            for s in practiced_skill_list:
                if s.success_count > 0:
                    successful_attempts_count += s.success_count
                    if s.hint_count == 0:
                        independent_success_count += s.success_count
                    hint_lvl = min(4, s.hint_count) if s.hint_count > 0 else 0
                    hint_levels_recorded.extend([hint_lvl] * s.success_count)
                elif s.failure_count > 0:
                    hint_levels_recorded.extend([min(4, s.hint_count)] * s.failure_count)

        independent_solution_rate = (
            round(independent_success_count / successful_attempts_count, 2)
            if successful_attempts_count > 0
            else None
        )

        average_hint_level = (
            round(sum(hint_levels_recorded) / len(hint_levels_recorded), 1)
            if hint_levels_recorded
            else None
        )

        is_empty = (practiced_skills_count == 0 and total_attempts_count == 0)

        return StudentProgressDashboardResponse(
            total_skills=mastery_summary.total_skills,
            practiced_skills=practiced_skills_count,
            current_mastery_estimate=current_mastery_estimate,
            is_empty=is_empty,
            strong_topics=strong_topics,
            topics_needing_practice=needing_practice,
            all_skills=all_skills,
            recent_attempts=recent_attempts,
            average_hint_level=average_hint_level,
            independent_solution_rate=independent_solution_rate,
            total_attempts_count=total_attempts_count,
            independent_success_count=independent_success_count,
        )

