from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class Preference(Base):
    __tablename__ = "preferences"
    __table_args__ = (UniqueConstraint("user_id", name="uq_preferences_user_id"),)

    id = Column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4()), index=True)
    user_id = Column(Uuid(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    language = Column(String(10), default="vi", nullable=False)
    notification_enabled = Column(Boolean, default=True, nullable=False)
    theme = Column(String(20), default="light", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="preference")
