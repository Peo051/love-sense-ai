from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class Consent(Base):
    __tablename__ = "consents"
    __table_args__ = (UniqueConstraint("user_id", "consent_type", name="uq_consents_user_type"),)

    id = Column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4()), index=True)
    user_id = Column(Uuid(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    history_enabled = Column(Boolean, default=True, nullable=False)
    save_input = Column(Boolean, default=False, nullable=False)
    save_result = Column(Boolean, default=False, nullable=False)
    consent_type = Column(String(80), default="analysis_history", nullable=False)
    is_accepted = Column(Boolean, default=False, nullable=False)
    accepted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="consents")
