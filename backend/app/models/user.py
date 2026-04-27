from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


def generate_uuid() -> str:
    return str(uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=False), primary_key=True, default=generate_uuid, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    profile = relationship("Profile", back_populates="user", cascade="all, delete-orphan", uselist=False)
    partner_profile = relationship("PartnerProfile", back_populates="user", cascade="all, delete-orphan", uselist=False)
    preference = relationship("Preference", back_populates="user", cascade="all, delete-orphan", uselist=False)
    consents = relationship("Consent", back_populates="user", cascade="all, delete-orphan")
    analysis_sessions = relationship("AnalysisSession", back_populates="user", cascade="all, delete-orphan")
