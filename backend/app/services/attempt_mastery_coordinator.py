from datetime import datetime, timezone
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.learning_session import LearningSession, StudentAttempt
from app.models.mastery_audit import StudentMasteryAudit
from app.models.student_skill_mastery import StudentSkillMastery
from app.services.mastery_store import MasteryRepository
from app.tutor.mastery import DeterministicMasteryModel, MasteryEvent
from app.tutor.skill_taxonomy import SkillTaxonomy

logger = logging.getLogger(__name__)


class AttemptMasteryCoordinator:
    """
    Điều phối viên kết nối các lần thử làm bài (StudentAttempt) với cập nhật độ thuần thục (StudentSkillMastery).

    NGUYÊN TẮC CỐT LÕI (APT-019):
    1. Không cập nhật điểm chỉ từ một chẩn đoán chưa xác minh (unverified model diagnosis alone).
    2. Cập nhật chỉ diễn ra khi lần thử đạt tới một kết quả tương tác thực tế (resolved, failed, solution_revealed).
    3. Giao dịch nguyên khối (Transactional): Lần thử, điểm mastery và audit log được lưu trong cùng transaction.
    4. Chống cập nhật trùng lặp (Duplicate-event / Replay protection): Replaying cùng một event không làm tăng điểm hay số đếm lần 2.
    5. Lưu vết kiểm toán chi tiết: previous_score, new_score, event_type, attempt_id, reason.
    """

    @classmethod
    async def resolve_attempt_and_update_mastery(
        cls,
        db: AsyncSession,
        *,
        user_id: str,
        attempt_id: str,
        outcome: str,
        highest_hint_level: int = 0,
        solution_revealed: bool = False,
        hints_used: int = 0,
        custom_reason: Optional[str] = None,
    ) -> tuple[Optional[StudentAttempt], list[StudentMasteryAudit]]:
        """
        Xác nhận kết quả của một lần thử bài và cập nhật độ thuần thục kỹ năng giao dịch.
        Bảo đảm tính idempotent: Nếu attempt_id đã từng được cập nhật mastery, hàm sẽ trả về
        các bản ghi audit đã có mà không áp dụng delta lần thứ hai.
        """
        # 1. Truy vấn lần thử và xác thực quyền sở hữu của người dùng qua session
        stmt_attempt = (
            select(StudentAttempt)
            .join(LearningSession, StudentAttempt.session_id == LearningSession.id)
            .where(
                StudentAttempt.id == attempt_id,
                LearningSession.user_id == user_id,
            )
            .options(selectinload(StudentAttempt.mastery_audits))
        )
        res_attempt = await db.execute(stmt_attempt)
        attempt = res_attempt.scalar_one_or_none()
        if not attempt:
            logger.warning(
                "Không tìm thấy attempt %s hoặc user %s không có quyền sở hữu.",
                attempt_id,
                user_id,
            )
            return None, []

        # 2. KIỂM TRA CHỐNG LẶP (Duplicate-event / Idempotency protection)
        # Nếu lần thử này đã từng ghi nhận audit mastery, tuyệt đối không double-update!
        stmt_audit_check = (
            select(StudentMasteryAudit)
            .where(
                StudentMasteryAudit.attempt_id == attempt_id,
                StudentMasteryAudit.user_id == user_id,
            )
            .order_by(StudentMasteryAudit.created_at)
        )
        res_audit_check = await db.execute(stmt_audit_check)
        existing_audits = list(res_audit_check.scalars().all())

        if existing_audits:
            logger.info(
                "Lần thử %s đã được ghi nhận mastery audit trước đó (%d bản ghi). Bỏ qua cập nhật trùng lặp (Idempotency).",
                attempt_id,
                len(existing_audits),
            )
            return attempt, existing_audits

        # 3. Phân loại sự kiện sư phạm (Pedagogical Event Classification)
        norm_outcome = outcome.strip().lower()
        is_resolved = norm_outcome in ("resolved", "likely_resolved", "success", "completed")

        event = DeterministicMasteryModel.classify_attempt_event(
            resolved=is_resolved,
            highest_hint_level_used=highest_hint_level,
            solution_revealed=solution_revealed,
        )

        # 4. Trích xuất các kỹ năng liên quan từ diagnosis của attempt
        skills_to_update: list[str] = []
        if isinstance(attempt.diagnosis, dict):
            raw_kc = attempt.diagnosis.get("knowledge_components") or []
            skills_to_update = SkillTaxonomy.map_knowledge_components(raw_kc)

        if not skills_to_update:
            # Fallback an toàn tới kỹ năng nền tảng nếu diagnosis không có thông tin
            skills_to_update = ["csharp.class_object"]

        # 5. Cập nhật giao dịch Mastery và tạo Audit Log
        timestamp = datetime.now(timezone.utc)
        audit_records: list[StudentMasteryAudit] = []

        for skill_code in skills_to_update:
            mastery_rec = await MasteryRepository.get_or_create_mastery(db, user_id, skill_code)
            previous_score = mastery_rec.mastery_score

            new_state = DeterministicMasteryModel.apply_event_to_state(
                current_score=previous_score,
                success_count=mastery_rec.success_count,
                failure_count=mastery_rec.failure_count,
                hint_count=mastery_rec.hint_count,
                event=event,
                hints_used_in_attempt=hints_used,
                practice_time=timestamp,
            )

            # Cập nhật bản ghi mastery
            mastery_rec.mastery_score = new_state["mastery_score"]
            mastery_rec.success_count = new_state["success_count"]
            mastery_rec.failure_count = new_state["failure_count"]
            mastery_rec.hint_count = new_state["hint_count"]
            mastery_rec.last_practiced_at = new_state["last_practiced_at"]

            # Xây dựng lý do kiểm toán (Audit Reason)
            reason_text = custom_reason or (
                f"Lần thử {attempt_id} kết thúc với trạng thái '{outcome}'. "
                f"Sự kiện xác định: '{event.value}'. "
                f"Điểm thuần thục thay đổi từ {previous_score:.4f} sang {mastery_rec.mastery_score:.4f}."
            )

            audit_entry = StudentMasteryAudit(
                user_id=user_id,
                skill_id=skill_code,
                attempt_id=attempt.id,
                event_type=event.value,
                previous_score=previous_score,
                new_score=mastery_rec.mastery_score,
                reason=reason_text,
                created_at=timestamp,
            )
            db.add(audit_entry)
            audit_records.append(audit_entry)

        # 6. Cập nhật trạng thái của lần thử
        attempt.success_state = outcome
        if hint_progression_update := {
            "highest_hint_level_used": highest_hint_level,
            "solution_revealed": solution_revealed,
            "hints_used": hints_used,
        }:
            existing_prog = dict(attempt.hint_progression or {})
            existing_prog.update(hint_progression_update)
            attempt.hint_progression = existing_prog

        # 7. Commit toàn bộ giao dịch
        await db.commit()
        await db.refresh(attempt)
        for audit in audit_records:
            await db.refresh(audit)

        logger.info(
            "Đã ghi nhận thành công mastery update cho attempt %s: event=%s, %d kỹ năng được cập nhật.",
            attempt_id,
            event.value,
            len(audit_records),
        )
        return attempt, audit_records

    @classmethod
    async def get_attempt_audits(
        cls,
        db: AsyncSession,
        user_id: str,
        attempt_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[StudentMasteryAudit]:
        """Lấy danh sách các bản ghi kiểm toán mastery của người dùng."""
        stmt = (
            select(StudentMasteryAudit)
            .where(StudentMasteryAudit.user_id == user_id)
        )
        if attempt_id:
            stmt = stmt.where(StudentMasteryAudit.attempt_id == attempt_id)

        stmt = stmt.order_by(StudentMasteryAudit.created_at.desc()).limit(limit).offset(offset)
        res = await db.execute(stmt)
        return list(res.scalars().all())
