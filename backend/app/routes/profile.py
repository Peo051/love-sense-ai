from fastapi import APIRouter

from app.schemas.profile_schema import ProfileResponse, ProfileUpsert
from app.services.memory_store import ProfileService

router = APIRouter()


@router.get("/profile", response_model=ProfileResponse)
async def get_profile():
    return ProfileService.get_profile()


@router.post("/profile", response_model=ProfileResponse)
async def save_profile(profile: ProfileUpsert):
    return ProfileService.save_profile(profile)


@router.delete("/profile")
async def delete_profile():
    ProfileService.delete_profile()
    return {"deleted": True}
