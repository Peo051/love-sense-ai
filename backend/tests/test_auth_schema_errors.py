import asyncio
from unittest.mock import AsyncMock
from sqlalchemy.exc import ProgrammingError

import app.deps.auth as auth_deps


def _missing_firebase_uid_error() -> ProgrammingError:
    return ProgrammingError(
        "SELECT users.firebase_uid FROM users",
        {},
        Exception("column users.firebase_uid does not exist"),
    )


async def _raise_missing_firebase_uid_column(*args, **kwargs):
    raise _missing_firebase_uid_error()


from fastapi.security import HTTPAuthorizationCredentials


def test_optional_auth_falls_back_to_guest_when_firebase_uid_column_is_missing(monkeypatch):
    monkeypatch.setattr(auth_deps, "_resolve_current_user", _raise_missing_firebase_uid_column)

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="firebase-token")
    user = asyncio.run(auth_deps.get_optional_user(credentials=credentials, db=AsyncMock()))
    assert user is None


def test_required_auth_returns_clear_schema_error_when_firebase_uid_column_is_missing(client, monkeypatch):
    monkeypatch.setattr(auth_deps, "_resolve_current_user", _raise_missing_firebase_uid_column)

    response = client.get("/api/me", headers={"Authorization": "Bearer firebase-token"})

    assert response.status_code == 503
    assert response.json()["detail"] == auth_deps.MISSING_FIREBASE_UID_SCHEMA_DETAIL

