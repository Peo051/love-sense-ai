from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


def generate_uuid() -> str:
    return str(uuid4())


class StudentMasteryAudit(Base):
    """
    Bảng lưu vết kiểm toán biến động điểm thuần thục kỹ năng (Student Mastery Audit).
    Bảo đảm Acceptance: Replaying the same event cannot double-update mastery
    nhờ ràng buộc UNIQUE(attempt_id, skill_id).
    """
    __tablename__ = "student_mastery_audit"
    __table_args__ = (
        UniqueConstraint("attempt_id", "skill_id", name="uq_mastery_audit_attempt_skill"),
        CheckConstraint("previous_score >= 0.0 AND previous_score <= 1.0", name="ck_mastery_audit_prev_score"),
        CheckConstraint("new_score >= 0.0 AND new_score <= 1.0", name="ck_mastery_audit_new_score"),
    )

    id = Column(Uuid(as_uuid=False), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(
        Uuid(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id = Column(
        String(50),
        ForeignKey("skills.code", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    attempt_id = Column(
        Uuid(as_uuid=False),
        ForeignKey("student_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type = Column(String(50), nullable=False)
    previous_score = Column(Float, nullable=False)
    new_score = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User")
    skill = relationship("SkillModel")
    attempt = relationship("StudentAttempt", back_populates="mastery_audits")
