from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    if database_url.startswith("sqlite://"):
        return database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return database_url


def is_sqlite_database_url(database_url: str) -> bool:
    return normalize_database_url(database_url).startswith("sqlite+aiosqlite://")


engine = create_async_engine(normalize_database_url(settings.database_url), echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_database_for_development() -> None:
    if settings.app_env != "development" or not settings.database_auto_create:
        return
    if not is_sqlite_database_url(settings.database_url):
        return

    # Chỉ tự tạo bảng cho SQLite dev fallback. PostgreSQL/Supabase vẫn dùng SQL migrations trong database/.
    import app.models  # noqa: F401

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
