from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, JSON, String, Text, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id = Column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4()), index=True)
    user_id = Column(Uuid(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    overall_emotion = Column(String(120), nullable=False)
    confidence = Column(Float, nullable=False)
    emotion_distribution = Column(JSON, nullable=False, default=dict)
    summary = Column(Text, nullable=False)
    context_note = Column(Text, nullable=False)
    suggested_reply = Column(Text, nullable=False)
    warning = Column(Text, nullable=False)
    save_input = Column(Boolean, default=False, nullable=False)
    save_result = Column(Boolean, default=False, nullable=False)
    consent_type = Column(String(80), default="analysis_history", nullable=False)
    is_accepted = Column(Boolean, default=False, nullable=False)
    accepted_at = Column(DateTime(timezone=True))
    chat_text = Column(Text)

    user = relationship("User", back_populates="analysis_sessions")
