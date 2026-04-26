from pydantic import BaseModel
from typing import Optional

class ProfileCreate(BaseModel):
    name: str
    age: int
    communication_style: str

class ProfileResponse(BaseModel):
    id: str
    name: str
    age: int
    communication_style: str

class PartnerProfileCreate(BaseModel):
    name: str
    age: int

class PreferenceCreate(BaseModel):
    language: str
    notification_enabled: bool = True
