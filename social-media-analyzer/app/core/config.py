from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/social_media_db"
    # SECRET_KEY and ENCRYPTION_KEY have no safe defaults; they MUST be set via
    # environment variables or .env file before running in any environment.
    SECRET_KEY: str
    REDIS_URL: str = "redis://localhost:6379/0"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ENCRYPTION_KEY: str  # 32-byte base64-url-safe key for Fernet encryption
    ALGORITHM: str = "HS256"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
