"""Application configuration management."""
from functools import lru_cache
from typing import Optional

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "RS Fruit Bites"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: PostgresDsn
    database_echo: bool = False

    # Business Logic
    basic_rate: float = 40.0
    medium_rate: float = 60.0
    premium_rate: float = 80.0

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, v: Optional[str]) -> str:
        """Validate database URL format."""
        if not v:
            raise ValueError("DATABASE_URL must be set")
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
