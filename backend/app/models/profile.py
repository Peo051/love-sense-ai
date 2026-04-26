from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4()), index=True)
    user_id = Column(Uuid(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    nickname = Column(String(80), default="", nullable=False)
    primary_language = Column(String(80), default="Tiếng Việt", nullable=False)
    communication_style = Column(String(120), default="", nullable=False)
    relationship_status = Column(String(120), default="", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="profile")
