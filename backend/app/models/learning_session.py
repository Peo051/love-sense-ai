from uuid import uuid4

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, JSON, String, Text, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


def generate_uuid() -> str:
    return str(uuid4())


class LearningSession(Base):
    """
    Phiên học tập lập trình C# OOP đa lượt của sinh viên (Multi-turn Learning Session).
    Quản lý tập trung các lần thử làm bài (attempts) và các thông điệp trao đổi (messages).
    """
    __tablename__ = "learning_sessions"

    id = Column(Uuid(as_uuid=False), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(Uuid(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    language = Column(String(50), default="csharp", nullable=False)
    topic = Column(String(100), nullable=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="learning_sessions")
    attempts = relationship(
        "StudentAttempt",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="StudentAttempt.created_at",
    )
    messages = relationship(
        "TutorMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="TutorMessage.created_at",
    )


class StudentAttempt(Base):
    """
    Lần thử làm bài của sinh viên trong phiên học (Student Attempt).
    Đảm bảo nguyên tắc riêng tư: Tuyệt đối không lưu raw student code trừ khi save_input là True.
    """
    __tablename__ = "student_attempts"
    __table_args__ = (
        CheckConstraint(
            "student_code IS NULL OR save_input IS TRUE",
            name="ck_student_attempts_code_requires_consent",
        ),
    )

    id = Column(Uuid(as_uuid=False), primary_key=True, default=generate_uuid, index=True)
    session_id = Column(Uuid(as_uuid=False), ForeignKey("learning_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_reference = Column(Text, nullable=False)
    diagnosis = Column(JSON, nullable=True)
    hint_progression = Column(JSON, nullable=True)
    success_state = Column(String(50), default="in_progress", nullable=False)
    save_input = Column(Boolean, default=False, nullable=False)
    student_code = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    session = relationship("LearningSession", back_populates="attempts")
    messages = relationship("TutorMessage", back_populates="attempt")
    mastery_audits = relationship(
        "StudentMasteryAudit",
        back_populates="attempt",
        cascade="all, delete-orphan",
    )


class TutorMessage(Base):
    """
    Tin nhắn trong chuỗi hội thoại đa lượt của phiên học (Tutor Message).
    Có thể liên kết với một lần thử làm bài cụ thể hoặc xuyên suốt phiên học.
    """
    __tablename__ = "tutor_messages"

    id = Column(Uuid(as_uuid=False), primary_key=True, default=generate_uuid, index=True)
    session_id = Column(Uuid(as_uuid=False), ForeignKey("learning_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    attempt_id = Column(Uuid(as_uuid=False), ForeignKey("student_attempts.id", ondelete="SET NULL"), nullable=True, index=True)
    role = Column(String(30), nullable=False)  # student, tutor, system
    sanitized_textual_message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    session = relationship("LearningSession", back_populates="messages")
    attempt = relationship("StudentAttempt", back_populates="messages")
