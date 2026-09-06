from datetime import datetime, timezone
import logging
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.learning_session import LearningSession, StudentAttempt, TutorMessage
from app.schemas.session_schema import (
    AttemptCreateRequest,
    MessageCreateRequest,
    SessionCreateRequest,
    SessionDetailResponse,
    SessionSummaryResponse,
    StudentAttemptResponse,
    TutorMessageResponse,
)

logger = logging.getLogger(__name__)


class SessionRepository:
    """
    Data access layer quản lý Multi-turn Learning Sessions.
    Đảm bảo 100% Strict User Ownership và Privacy Invariant.
    """

    @staticmethod
    async def create_session(
        db: AsyncSession,
        user_id: str,
        request: SessionCreateRequest,
    ) -> SessionDetailResponse:
        """Khởi tạo phiên học tập mới kèm attempt và tin nhắn mở đầu nếu có."""
        session = LearningSession(
            user_id=user_id,
            title=request.title,
            language=request.language,
            topic=request.topic,
        )
        db.add(session)
        await db.flush()

        if request.initial_problem or request.initial_code:
            # Privacy Invariant: Tuyệt đối không lưu raw student code nếu save_input là False
            code_to_store = request.initial_code if request.save_input else None
            initial_attempt = StudentAttempt(
                session_id=session.id,
                problem_reference=request.initial_problem or "Khởi tạo bài tập C# OOP",
                student_code=code_to_store,
                save_input=request.save_input,
                success_state="in_progress",
            )
            db.add(initial_attempt)
            await db.flush()

            initial_msg = TutorMessage(
                session_id=session.id,
                attempt_id=initial_attempt.id,
                role="system",
                sanitized_textual_message=f"Bắt đầu phiên học tập: {request.title}",
            )
            db.add(initial_msg)

        await db.commit()
        detailed = await SessionRepository.get_user_session(db, user_id=user_id, session_id=session.id)
        if not detailed:
            raise RuntimeError("Không thể tải thông tin phiên học vừa tạo.")
        return detailed

    @staticmethod
    async def list_user_sessions(
        db: AsyncSession,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[SessionSummaryResponse]:
        """Lấy danh sách phiên học của người dùng hiện tại (Strict user ownership)."""
        query = (
            select(LearningSession)
            .where(LearningSession.user_id == user_id)
            .options(
                selectinload(LearningSession.attempts),
                selectinload(LearningSession.messages),
            )
            .order_by(LearningSession.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(query)
        sessions = result.scalars().all()
        return [
            SessionSummaryResponse(
                id=s.id,
                user_id=s.user_id,
                language=s.language,
                topic=s.topic,
                title=s.title,
                created_at=s.created_at,
                updated_at=s.updated_at,
                attempt_count=len(s.attempts),
                message_count=len(s.messages),
            )
            for s in sessions
        ]

    @staticmethod
    async def get_user_session(
        db: AsyncSession,
        user_id: str,
        session_id: str,
    ) -> Optional[SessionDetailResponse]:
        """Lấy chi tiết một phiên học theo ID với kiểm tra quyền sở hữu tuyệt đối."""
        query = (
            select(LearningSession)
            .where(
                LearningSession.id == session_id,
                LearningSession.user_id == user_id,
            )
            .options(
                selectinload(LearningSession.attempts),
                selectinload(LearningSession.messages),
            )
        )
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        if not session:
            return None

        return SessionDetailResponse(
            id=session.id,
            user_id=session.user_id,
            language=session.language,
            topic=session.topic,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            attempt_count=len(session.attempts),
            message_count=len(session.messages),
            attempts=[
                StudentAttemptResponse(
                    id=a.id,
                    session_id=a.session_id,
                    problem_reference=a.problem_reference,
                    diagnosis=a.diagnosis,
                    hint_progression=a.hint_progression,
                    success_state=a.success_state,
                    save_input=a.save_input,
                    # Privacy check kép: chỉ hiển thị student_code nếu save_input là True
                    student_code=a.student_code if a.save_input else None,
                    created_at=a.created_at,
                )
                for a in session.attempts
            ],
            messages=[
                TutorMessageResponse(
                    id=m.id,
                    session_id=m.session_id,
                    attempt_id=m.attempt_id,
                    role=m.role,
                    sanitized_textual_message=m.sanitized_textual_message,
                    created_at=m.created_at,
                )
                for m in session.messages
            ],
        )

    @staticmethod
    async def delete_user_session(
        db: AsyncSession,
        user_id: str,
        session_id: str,
    ) -> bool:
        """Xóa một phiên học (cascade attempts và messages). Chỉ xóa khi đúng user_id."""
        query = select(LearningSession).where(
            LearningSession.id == session_id,
            LearningSession.user_id == user_id,
        )
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        if not session:
            return False

        await db.delete(session)
        await db.commit()
        logger.info("Đã xóa phiên học %s của user %s", session_id, user_id)
        return True

    @staticmethod
    async def add_attempt(
        db: AsyncSession,
        user_id: str,
        session_id: str,
        request: AttemptCreateRequest,
    ) -> Optional[StudentAttemptResponse]:
        """Thêm lần thử bài mới vào phiên học."""
        query = select(LearningSession).where(
            LearningSession.id == session_id,
            LearningSession.user_id == user_id,
        )
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        if not session:
            return None

        # Privacy invariant
        code_to_store = request.student_code if request.save_input else None
        attempt = StudentAttempt(
            session_id=session.id,
            problem_reference=request.problem_reference,
            student_code=code_to_store,
            save_input=request.save_input,
            diagnosis=request.diagnosis,
            hint_progression=request.hint_progression,
            success_state=request.success_state,
        )
        db.add(attempt)
        session.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(attempt)
        return StudentAttemptResponse.model_validate(attempt)

    @staticmethod
    async def add_message(
        db: AsyncSession,
        user_id: str,
        session_id: str,
        request: MessageCreateRequest,
    ) -> Optional[TutorMessageResponse]:
        """Thêm tin nhắn văn bản đã làm sạch vào chuỗi hội thoại của phiên học."""
        query = select(LearningSession).where(
            LearningSession.id == session_id,
            LearningSession.user_id == user_id,
        )
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        if not session:
            return None

        message = TutorMessage(
            session_id=session.id,
            attempt_id=request.attempt_id,
            role=request.role,
            sanitized_textual_message=request.content.strip(),
        )
        db.add(message)
        session.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(message)
        return TutorMessageResponse.model_validate(message)
