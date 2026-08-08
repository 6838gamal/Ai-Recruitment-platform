"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from typing import List, Optional

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field 

_PLACEHOLDER_KEY = "change-me-in-production-use-64-random-hex-chars"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Application ─────────────────────────────────────────────────
    APP_NAME: str = "AI Recruitment Platform"
    APP_ENV: str = "development"  # development | staging | production
    DEBUG: bool = True
    #SECRET_KEY: str = _PLACEHOLDER_KEY
    # Allow SESSION_SECRET (Replit-provisioned) as an alias for SECRET_KEY
    #SESSION_SECRET: Optional[str] = None

    SECRET_KEY: str = Field(default=_PLACEHOLDER_KEY, validation_alias="SECRET_KEY")
    SESSION_SECRET: Optional[str] = Field(default=None, validation_alias="SESSION_SECRET")
    ALLOWED_HOSTS: str = "*"

    @model_validator(mode="after")
    def resolve_secret_key(self) -> "Settings":
        """Use SESSION_SECRET as SECRET_KEY when SECRET_KEY is unset/placeholder."""
        if self.SECRET_KEY == _PLACEHOLDER_KEY and self.SESSION_SECRET:
            self.SECRET_KEY = self.SESSION_SECRET
        if self.SECRET_KEY == _PLACEHOLDER_KEY and self.APP_ENV != "development":
            raise ValueError(
                "SECRET_KEY must be set to a secure random value outside development. "
                "Set SECRET_KEY or SESSION_SECRET in your environment/secrets."
            )
        return self

    # ─── Database ────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://gamalalmaqtary:mfpNMrFTCQlurkpwuCXj88w3A042Z7hc@dpg-d9reg07avr4c7392ub3g-a.virginia-postgres.render.com/ai_recruitment_platform_db"

    # ─── JWT / Security ──────────────────────────────────────────────
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─── CORS ────────────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:5000"

    # ─── Email (SMTP) ────────────────────────────────────────────────
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    FROM_EMAIL: str = "noreply@example.com"
    FROM_NAME: str = "AI Recruitment Platform"

    # ─── AI Provider ─────────────────────────────────────────────────
    AI_PROVIDER: str = "openai"  # openai | anthropic | local
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-4o-mini"
    AI_BASE_URL: Optional[str] = None  # for local LLM

    # ─── File Storage ────────────────────────────────────────────────
    STORAGE_BACKEND: str = "local"  # local | s3 | supabase
    LOCAL_UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # AWS S3
    S3_BUCKET: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None

    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_BUCKET: Optional[str] = None

    # ─── WhatsApp ────────────────────────────────────────────────────
    WHATSAPP_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_ID: Optional[str] = None

    # ─── Pagination ──────────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = 25
    MAX_PAGE_SIZE: int = 100

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def allowed_hosts_list(self) -> List[str]:
        return [h.strip() for h in self.ALLOWED_HOSTS.split(",")]

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
