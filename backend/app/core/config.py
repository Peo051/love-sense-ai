from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    APP_ENV: str = "development"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Love Emotion API"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/loveemotion"
    
    # AI Service
    AI_SERVICE_URL: str = "http://localhost:8001"
    
    # LLM Configuration
    LLM_PROVIDER: str = "openai"
    LLM_BASE_URL: str = ""
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_MOCK_MODE: bool = True
    LLM_TIMEOUT_SECONDS: float = 30.0

    # Security
    SECRET_KEY: str = "dev-only-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
