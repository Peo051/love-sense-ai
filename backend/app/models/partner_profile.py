from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class PartnerProfile(Base):
    __tablename__ = "partner_profiles"

    id = Column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4()), index=True)
    user_id = Column(Uuid(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    nickname = Column(String(80), default="", nullable=False)
    likes = Column(Text, default="", nullable=False)
    dislikes = Column(Text, default="", nullable=False)
    texting_style = Column(Text, default="", nullable=False)
    when_happy = Column(Text, default="", nullable=False)
    when_sad = Column(Text, default="", nullable=False)
    when_angry = Column(Text, default="", nullable=False)
    likes_checkins = Column(Boolean, default=True, nullable=False)
    dislikes_repeated_questions = Column(Boolean, default=True, nullable=False)
    height_cm = Column(Float)
    weight_kg = Column(Float)
    appearance = Column(Text, default="", nullable=False)
    private_notes = Column(Text, default="", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="partner_profile")
