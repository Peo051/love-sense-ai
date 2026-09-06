from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.profile_schema import ProfileResponse, ProfileUpsert
from app.services.db_store import ProfileRepository

router = APIRouter()


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ProfileRepository.get_profile(db, current_user.id)


@router.post("/profile", response_model=ProfileResponse)
async def save_profile(
    profile: ProfileUpsert,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ProfileRepository.save_profile(db, current_user.id, profile)


@router.delete("/profile")
async def delete_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ProfileRepository.delete_profile(db, current_user.id)
    return {"deleted": True}
