from pydantic import AliasChoices, Field, ValidationInfo, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_FRONTEND_URL = "http://localhost:3000"
DEFAULT_ALLOWED_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000,https://love-sense-ai.vercel.app"
DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///./love_emotion_dev.db"


def _is_local_frontend_url(frontend_url: str) -> bool:
    normalized_url = frontend_url.strip().lower()
    return normalized_url.startswith(("http://localhost", "http://127.0.0.1"))


def _is_postgresql_database_url(database_url: str) -> bool:
    normalized_url = database_url.strip().lower()
    return normalized_url.startswith(("postgresql://", "postgres://", "postgresql+asyncpg://"))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    app_env: str = "development"
    frontend_url: str = DEFAULT_FRONTEND_URL

    api_v1_str: str = "/api/v1"
    project_name: str = "Love Emotion API"
    allowed_origins: str = DEFAULT_ALLOWED_ORIGINS

    database_url: str = DEFAULT_DATABASE_URL
    database_auto_create: bool = True
    ai_service_url: str = "http://localhost:8001"
    firebase_service_account_json: str = ""

    llm_provider: str = "mock"
    llm_base_url: str = "http://localhost:20128/v1"
    llm_api_key: str = ""
    llm_model: str = "api_models_all"
    llm_mock_mode: bool = True
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 2
    llm_retry_base_delay_seconds: float = 0.25
    vision_ocr_model: str = Field(
        default="",
        validation_alias=AliasChoices("VISION_MODEL", "VISION_OCR_MODEL"),
    )

    analyze_rate_limit_requests: int = Field(
        default=20,
        validation_alias=AliasChoices("RATE_LIMIT_MAX_REQUESTS", "ANALYZE_RATE_LIMIT_REQUESTS"),
    )
    analyze_rate_limit_window_seconds: int = Field(
        default=60,
        validation_alias=AliasChoices("RATE_LIMIT_WINDOW_SECONDS", "ANALYZE_RATE_LIMIT_WINDOW_SECONDS"),
    )

    secret_key: str = "dev-only-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @field_validator("database_auto_create", "llm_mock_mode", mode="before")
    @classmethod
    def use_default_for_blank_boolean(cls, value, info: ValidationInfo):
        if value == "":
            return cls.model_fields[info.field_name].default
        return value

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.app_env.strip().lower() != "production":
            return self

        if not self.frontend_url.strip() or _is_local_frontend_url(self.frontend_url):
            raise ValueError("APP_ENV=production requires FRONTEND_URL to be set to the deployed frontend URL.")

        if not self.database_url.strip() or not _is_postgresql_database_url(self.database_url):
            raise ValueError(
                "APP_ENV=production requires DATABASE_URL to point to PostgreSQL or Supabase. "
                "Do not use the SQLite development fallback in production."
            )

        if self.secret_key in {"", "dev-only-change-me", "change-this-for-local-dev"}:
            raise ValueError("APP_ENV=production requires SECRET_KEY to be set to a strong deployment secret.")

        return self

    @property
    def cors_origins(self) -> list[str]:
        origins = [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
        frontend_url = self.frontend_url.strip()

        if self.app_env.strip().lower() == "production" and self.allowed_origins.strip() == DEFAULT_ALLOWED_ORIGINS:
            origins = []

        if frontend_url and frontend_url not in origins:
            origins.append(frontend_url)
        return origins


settings = Settings()
