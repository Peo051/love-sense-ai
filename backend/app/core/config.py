from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    frontend_url: str = "http://localhost:3000"
    database_url: str = "postgresql://user:password@localhost/loveemotion"
    llm_provider: str = "openai"
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_mock_mode: bool = True

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Love Emotion API"

    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    AI_SERVICE_URL: str = "http://localhost:8001"

    SECRET_KEY: str = "dev-only-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def DATABASE_URL(self) -> str:  # noqa: N802 - keep compatibility with existing code
        return self.database_url

    @property
    def APP_ENV(self) -> str:  # noqa: N802 - optional uppercase compatibility
        return self.app_env

    @property
    def FRONTEND_URL(self) -> str:  # noqa: N802 - optional uppercase compatibility
        return self.frontend_url

    @property
    def LLM_PROVIDER(self) -> str:  # noqa: N802 - optional uppercase compatibility
        return self.llm_provider

    @property
    def LLM_BASE_URL(self) -> str:  # noqa: N802 - optional uppercase compatibility
        return self.llm_base_url

    @property
    def LLM_API_KEY(self) -> str:  # noqa: N802 - optional uppercase compatibility
        return self.llm_api_key

    @property
    def LLM_MODEL(self) -> str:  # noqa: N802 - optional uppercase compatibility
        return self.llm_model

    @property
    def LLM_MOCK_MODE(self) -> bool:  # noqa: N802 - optional uppercase compatibility
        return self.llm_mock_mode

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
