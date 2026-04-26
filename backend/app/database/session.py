from sqlalchemy.orm import Session
from app.database.connection import SessionLocal

def get_session() -> Session:
    """Get database session"""
    return SessionLocal()
