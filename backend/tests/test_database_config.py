import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.database.connection import is_sqlite_database_url, normalize_database_url


def test_database_url_normalization_supports_async_drivers():
    assert (
        normalize_database_url("postgresql://user:pass@localhost:5432/loveemotion")
        == "postgresql+asyncpg://user:pass@localhost:5432/loveemotion"
    )
    assert (
        normalize_database_url("postgres://user:pass@localhost:5432/loveemotion")
        == "postgresql+asyncpg://user:pass@localhost:5432/loveemotion"
    )
    assert normalize_database_url("sqlite:///./love_emotion_dev.db") == "sqlite+aiosqlite:///./love_emotion_dev.db"


def test_development_database_has_persistent_sqlite_fallback():
    default_database_url = Settings.model_fields["database_url"].default

    assert default_database_url == "sqlite+aiosqlite:///./love_emotion_dev.db"
    assert is_sqlite_database_url(default_database_url)


def test_production_rejects_sqlite_database_fallback():
    with pytest.raises(ValidationError, match="DATABASE_URL"):
        Settings(
            _env_file=None,
            app_env="production",
            frontend_url="https://frontend.example",
            database_url="sqlite+aiosqlite:///./love_emotion_dev.db",
            secret_key="strong-production-secret",
        )


def test_production_requires_deployed_frontend_url():
    with pytest.raises(ValidationError, match="FRONTEND_URL"):
        Settings(
            _env_file=None,
            app_env="production",
            frontend_url="http://localhost:3000",
            database_url="postgresql://user:pass@db.example:5432/loveemotion",
            secret_key="strong-production-secret",
        )


def test_rate_limit_env_aliases_are_supported(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_MAX_REQUESTS", "7")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SECONDS", "15")

    test_settings = Settings(_env_file=None)

    assert test_settings.analyze_rate_limit_requests == 7
    assert test_settings.analyze_rate_limit_window_seconds == 15


def test_production_cors_uses_frontend_url_without_localhost_defaults():
    test_settings = Settings(
        _env_file=None,
        app_env="production",
        frontend_url="https://frontend.example",
        database_url="postgresql://user:pass@db.example:5432/loveemotion",
        secret_key="strong-production-secret",
    )

    assert test_settings.cors_origins == ["https://frontend.example"]
