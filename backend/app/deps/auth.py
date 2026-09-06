import logging
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.firebase import initialize_firebase_admin, is_firebase_admin_initialized
from app.database.connection import get_db
from app.models.user import User
from app.schemas.auth_schema import TokenData
from app.services.db_store import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)
optional_bearer_scheme = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)

MISSING_FIREBASE_UID_SCHEMA_DETAIL = (
    "Database schema is missing users.firebase_uid. "
    "Run migration database/migrations/009_add_firebase_uid_to_users.sql."
)


@dataclass(frozen=True)
class CurrentUser:
    id: str
    uid: str
    email: str
    name: str | None = None
    picture: str | None = None
    is_active: bool = True


def _credentials_exception(detail: str = "Invalid or expired authentication token.") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _schema_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=MISSING_FIREBASE_UID_SCHEMA_DETAIL,
    )


def _is_missing_firebase_uid_schema_error(exc: BaseException) -> bool:
    pending: list[BaseException] = [exc]
    seen: set[int] = set()

    while pending:
        current = pending.pop(0)
        if id(current) in seen:
            continue
        seen.add(id(current))

        message = str(current).lower()
        if "firebase_uid" in message and (
            "undefinedcolumn" in message
            or "undefined column" in message
            or "no such column" in message
            or "does not exist" in message
        ):
            return True

        for nested in (
            getattr(current, "orig", None),
            getattr(current, "__cause__", None),
            getattr(current, "__context__", None),
        ):
            if isinstance(nested, BaseException):
                pending.append(nested)

    return False


async def _rollback_safely(db: AsyncSession) -> None:
    try:
        await db.rollback()
    except Exception:
        logger.warning("Failed to rollback auth database session after auth lookup error.")


def _to_current_user(user: User, *, uid: str | None = None, name: str | None = None, picture: str | None = None) -> CurrentUser:
    return CurrentUser(
        id=user.id,
        uid=uid or user.firebase_uid or user.id,
        email=user.email,
        name=name,
        picture=picture,
        is_active=user.is_active,
    )


async def _load_legacy_user_from_token(token: str, db: AsyncSession) -> CurrentUser:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        token_data = TokenData(user_id=payload.get("sub"), email=payload.get("email"))
    except JWTError as exc:
        raise _credentials_exception() from exc

    if token_data.user_id is None:
        raise _credentials_exception()

    result = await db.execute(select(User).where(User.id == token_data.user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if user is None:
        raise _credentials_exception()

    return _to_current_user(user)


async def _load_firebase_user_from_token(token: str, db: AsyncSession) -> CurrentUser:
    if not is_firebase_admin_initialized():
        initialize_firebase_admin()

    if not is_firebase_admin_initialized():
        raise _credentials_exception("Firebase Authentication is not configured on this backend.")

    try:
        decoded_token = firebase_auth.verify_id_token(token)
    except Exception as exc:  # Firebase SDK raises several auth-specific subclasses.
        raise _credentials_exception() from exc

    uid = str(decoded_token.get("uid") or "").strip()
    if not uid:
        raise _credentials_exception()

    email = str(decoded_token.get("email") or "").strip().lower() or f"{uid}@firebase.local"
    name = str(decoded_token.get("name") or "").strip() or None
    picture = str(decoded_token.get("picture") or "").strip() or None

    user = await UserRepository.get_or_create_firebase_user(
        db,
        firebase_uid=uid,
        email=email,
    )
    if not user.is_active:
        raise _credentials_exception("User account is inactive.")

    return _to_current_user(user, uid=uid, name=name, picture=picture)


async def _resolve_current_user(token: str, db: AsyncSession) -> CurrentUser:
    try:
        return await _load_legacy_user_from_token(token, db)
    except HTTPException:
        return await _load_firebase_user_from_token(token, db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    if credentials is None:
        raise _credentials_exception("Authentication token is required.")
    if credentials.scheme.lower() != "bearer":
        raise _credentials_exception()
    try:
        return await _resolve_current_user(credentials.credentials, db)
    except SQLAlchemyError as exc:
        await _rollback_safely(db)
        if _is_missing_firebase_uid_schema_error(exc):
            logger.error("Database schema is missing users.firebase_uid. Run migration 009 before authenticated routes.")
            raise _schema_exception() from exc
        logger.error("Database error while resolving authenticated user: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication storage is temporarily unavailable.",
        ) from exc


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser | None:
    if credentials is None:
        return None
    if credentials.scheme.lower() != "bearer":
        return None
    try:
        return await _resolve_current_user(credentials.credentials, db)
    except HTTPException:
        return None
    except SQLAlchemyError as exc:
        await _rollback_safely(db)
        if _is_missing_firebase_uid_schema_error(exc):
            logger.error(
                "Database schema is missing users.firebase_uid. Continuing optional auth request as guest; history will not be saved."
            )
            return None
        logger.warning("Optional auth lookup skipped after database error: %s", type(exc).__name__)
        return None
