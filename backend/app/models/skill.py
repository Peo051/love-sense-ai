from sqlalchemy import Column, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class SkillModel(Base):
    """
    Bảng lưu trữ taxonomy các kỹ năng lập trình (Skills Taxonomy).
    Tương ứng với migration 012_create_skills_taxonomy.sql.
    """
    __tablename__ = "skills"

    code = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    prerequisites = Column(JSON, default=list, nullable=False)
    difficulty = Column(Integer, nullable=False)
    taxonomy_version = Column(String(20), default="v1", nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    masteries = relationship(
        "StudentSkillMastery",
        back_populates="skill",
        cascade="all, delete-orphan",
    )
