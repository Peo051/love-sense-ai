from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str | None = None
    email: str | None = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    is_active: bool


class AuthMeResponse(UserResponse):
    uid: str
    name: str | None = None
    picture: str | None = None
