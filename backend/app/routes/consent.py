from fastapi import APIRouter

from app.schemas.consent_schema import ConsentSettings, ConsentUpdate
from app.services.memory_store import ConsentService

router = APIRouter()


@router.get("/consent", response_model=ConsentSettings)
async def get_consent():
    return ConsentService.get_consent()


@router.post("/consent", response_model=ConsentSettings)
async def save_consent(consent: ConsentUpdate):
    return ConsentService.save_consent(consent)
