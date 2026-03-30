from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/social_media_db"
    SECRET_KEY: str = "change-me-in-production-super-secret-key-32chars"
    REDIS_URL: str = "redis://localhost:6379/0"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ENCRYPTION_KEY: str = "Fk3dL9mN2pQrStUvWxYzAbCdEfGhIjKl"  # 32 chars for Fernet
    ALGORITHM: str = "HS256"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
