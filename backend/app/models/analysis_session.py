from sqlalchemy import Column, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base

class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    emotion = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    suggested_reply = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
