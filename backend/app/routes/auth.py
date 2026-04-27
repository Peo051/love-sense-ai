from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.database.connection import get_db
from app.deps.auth import CurrentUser, get_current_user
from app.schemas.auth_schema import AuthMeResponse, Token, UserCreate, UserResponse
from app.services.db_store import UserRepository

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await UserRepository.get_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email đã được đăng ký.")

    created_user = await UserRepository.create_user(
        db,
        email=user.email,
        hashed_password=get_password_hash(user.password),
    )
    return UserResponse(id=created_user.id, email=created_user.email, is_active=created_user.is_active)


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await UserRepository.get_by_email(db, form_data.username)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=AuthMeResponse)
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    return AuthMeResponse(
        id=current_user.id,
        uid=current_user.uid,
        email=current_user.email,
        name=current_user.name,
        picture=current_user.picture,
        is_active=current_user.is_active,
    )
