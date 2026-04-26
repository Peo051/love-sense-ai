import asyncio
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.database.connection import Base, get_db
from app.main import app
import app.models as app_models  # noqa: F401 - import models before metadata.create_all

test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


async def reset_database():
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


@pytest.fixture(autouse=True)
def test_runtime_settings(monkeypatch):
    monkeypatch.setattr(settings, "LLM_MOCK_MODE", True)
    monkeypatch.setattr(settings, "LLM_PROVIDER", "mock")


@pytest.fixture(autouse=True)
def database_override():
    asyncio.run(reset_database())
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    asyncio.run(reset_database())


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client: TestClient):
    email = f"user-{uuid4()}@example.com"
    password = "secret123"

    register_response = client.post("/api/register", json={"email": email, "password": password})
    assert register_response.status_code == 201

    token_response = client.post(
        "/api/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_response.status_code == 200

    token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
