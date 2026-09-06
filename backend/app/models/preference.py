from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Uuid
from sqlalchemy.sql import func

from app.database.connection import Base


class Preference(Base):
    __tablename__ = "preferences"

    id = Column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4()), index=True)
    user_id = Column(Uuid(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    language = Column(String, default="vi")
    notification_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
