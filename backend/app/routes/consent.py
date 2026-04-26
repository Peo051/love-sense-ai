from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.consent_schema import ConsentSettings, ConsentUpdate
from app.services.db_store import ConsentRepository

router = APIRouter()


@router.get("/consent", response_model=ConsentSettings)
async def get_consent(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ConsentRepository.get_consent(db, current_user.id, "privacy_settings")


@router.post("/consent", response_model=ConsentSettings)
async def save_consent(
    consent: ConsentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    normalized_consent = consent.model_copy(update={"consent_type": "privacy_settings"})
    return await ConsentRepository.save_consent(db, current_user.id, normalized_consent)
