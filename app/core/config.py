# app/core/config.py
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "WorkTodo API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"  # local, development, production

    # Sentry
    SENTRY_DSN: Optional[str] = None

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"  # Для локальной разработки

    # File Uploads
    UPLOAD_DIR: Path = Path("uploads")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
