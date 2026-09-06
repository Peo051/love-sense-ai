from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


def generate_uuid() -> str:
    return str(uuid4())


class StudentSkillMastery(Base):
    """
    Theo dõi mức độ thuần thục kỹ năng của sinh viên (Student Skill Mastery).
    Sử dụng luật cập nhật tất định, minh bạch (V1) với điểm khởi tạo trung tính 0.5.
    """
    __tablename__ = "student_skill_mastery"
    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", name="uq_student_skill_mastery_user_skill"),
        CheckConstraint(
            "mastery_score >= 0.0 AND mastery_score <= 1.0",
            name="ck_student_skill_mastery_score_bounds",
        ),
        CheckConstraint("success_count >= 0", name="ck_student_skill_mastery_success_count"),
        CheckConstraint("failure_count >= 0", name="ck_student_skill_mastery_failure_count"),
        CheckConstraint("hint_count >= 0", name="ck_student_skill_mastery_hint_count"),
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
    mastery_score = Column(Float, default=0.5, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    failure_count = Column(Integer, default=0, nullable=False)
    hint_count = Column(Integer, default=0, nullable=False)
    last_practiced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="skill_masteries")
    skill = relationship("SkillModel", back_populates="masteries")
