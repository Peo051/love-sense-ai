from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    nickname: str = Field(default="", max_length=80)
    primary_language: str = Field(default="Tiếng Việt", max_length=80)
    communication_style: str = Field(default="", max_length=120)
    relationship_status: str = Field(default="", max_length=120)


class PartnerProfile(BaseModel):
    nickname: str = Field(default="", max_length=80)
    likes: str = Field(default="", max_length=1000)
    dislikes: str = Field(default="", max_length=1000)
    texting_style: str = Field(default="", max_length=1000)
    when_happy: str = Field(default="", max_length=1000)
    when_sad: str = Field(default="", max_length=1000)
    when_angry: str = Field(default="", max_length=1000)
    likes_checkins: bool = True
    dislikes_repeated_questions: bool = True
    height_cm: Optional[float] = Field(
        default=None,
        ge=0,
        le=250,
        description="Thông tin tùy chọn, không dùng để suy luận cảm xúc.",
    )
    weight_kg: Optional[float] = Field(
        default=None,
        ge=0,
        le=300,
        description="Thông tin tùy chọn, không dùng để suy luận cảm xúc.",
    )
    appearance: str = Field(default="", max_length=1000)
    private_notes: str = Field(default="", max_length=2000)


class ProfileUpsert(BaseModel):
    user_profile: UserProfile
    partner_profile: PartnerProfile


class ProfileResponse(ProfileUpsert):
    updated_at: datetime
