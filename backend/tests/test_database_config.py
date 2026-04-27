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
