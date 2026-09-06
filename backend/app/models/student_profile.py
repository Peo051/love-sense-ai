from uuid import uuid4

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


def generate_uuid() -> str:
    return str(uuid4())


class StudentProfile(Base):
    """
    Hồ sơ học tập của sinh viên trong hệ thống gia sư lập trình thích ứng (Student Profile).
    Tách biệt hoàn toàn và không kế thừa bất kỳ thuộc tính tình cảm nào từ schema cũ.
    """
    __tablename__ = "student_profiles"
    __table_args__ = (
        CheckConstraint(
            "programming_language = 'csharp'",
            name="ck_student_profiles_language",
        ),
        CheckConstraint(
            "skill_level = 'beginner'",
            name="ck_student_profiles_skill_level",
        ),
        CheckConstraint(
            "preferred_explanation IN ('concise', 'step_by_step', 'example_first')",
            name="ck_student_profiles_preferred_explanation",
        ),
        CheckConstraint(
            "solution_preference IN ('hint_first', 'balanced')",
            name="ck_student_profiles_solution_preference",
        ),
    )

    id = Column(Uuid(as_uuid=False), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(
        Uuid(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    display_name = Column(String(100), nullable=True)
    programming_language = Column(String(50), default="csharp", nullable=False)
    skill_level = Column(String(50), default="beginner", nullable=False)
    current_course = Column(String(120), nullable=True)
    preferred_explanation = Column(String(50), default="step_by_step", nullable=False)
    solution_preference = Column(String(50), default="hint_first", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship
    user = relationship("User", back_populates="student_profile")
