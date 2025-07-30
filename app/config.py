# app/core/config.py
from dataclasses import Field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent


# SECRET_KEY=gV64m9aIzFG4qpgVphvQbPQrtAO0nM-7YwwOvu0XPt5KJOjAy4AfgLkqJXYEt
# ALGORITHM=HS256
class JWTAuth(BaseModel):
    PRIVATE_KEY: str = (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"  # todo сгенерить ключ самостоятельно с помощью опенссл
    )
    PUBLIC_KEY_PATH: str = (
        "4f1a7c1a59f91cdd76b8705be5f5c9c86ebd942ebd4136a473b28fa8f70b17cd"  # todo сделать подтягивание из env или из файлов
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30


class Settings(BaseSettings):
    PROJECT_NAME: str = "TaskMaster API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"  # local, development, production

    # Sentry
    SENTRY_DSN: Optional[str] = None

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Database
    SQLITE_DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    POSTGRE_DATABASE_URL: str = (
        "postgresql+asyncpg://dbuser:dbpassword@localhost:5432/taskmaster"
    )

    # JWT
    JWT: JWTAuth = JWTAuth()

    # File Uploads
    UPLOAD_DIR: Path = Path("uploads")

    ORGANISATION_MAP: Dict[str, str] = {
        "p17": "ГП 17",
    }

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
