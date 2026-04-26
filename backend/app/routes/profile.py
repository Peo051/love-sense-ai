from fastapi import APIRouter, Depends, HTTPException
from app.schemas.profile_schema import ProfileCreate, ProfileResponse
from typing import List

router = APIRouter()

@router.post("/profile", response_model=ProfileResponse)
async def create_profile(profile: ProfileCreate):
    # TODO: Save to database
    return ProfileResponse(
        id="1",
        name=profile.name,
        age=profile.age,
        communication_style=profile.communication_style
    )

@router.get("/profile/{user_id}", response_model=ProfileResponse)
async def get_profile(user_id: str):
    # TODO: Get from database
    return ProfileResponse(
        id=user_id,
        name="User",
        age=25,
        communication_style="direct"
    )
