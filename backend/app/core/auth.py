from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.connection import get_db
from app.models.user import User
from app.schemas.auth_schema import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token", auto_error=False)


async def _load_user_from_token(token: str, db: AsyncSession) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực người dùng.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenData(user_id=payload.get("sub"), email=payload.get("email"))
    except JWTError as exc:
        raise credentials_exception from exc

    if token_data.user_id is None:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == token_data.user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    return await _load_user_from_token(token, db)


async def get_optional_current_user(
    token: str | None = Depends(optional_oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if not token:
        return None
    return await _load_user_from_token(token, db)
