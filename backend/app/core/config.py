from typing import List, Union, Optional
from pydantic import AnyHttpUrl, validator, computed_field
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
import json
from functools import lru_cache
from pathlib import Path

load_dotenv()

class Settings(BaseSettings):
    # Base Configuration
    PROJECT_NAME: str = "Shopify AI Image App"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Shopify Configuration
    SHOPIFY_API_KEY: Optional[str] = None
    SHOPIFY_API_SECRET: Optional[str] = None
    SHOPIFY_APP_URL: Optional[str] = os.getenv("SHOPIFY_APP_URL")
    SHOPIFY_SCOPES: str = os.getenv("SHOPIFY_SCOPES", "write_products,write_files,read_files")
    SHOPIFY_API_VERSION: str = "2024-01"  # Latest stable version

    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
    
    # Supabase Database Configuration
    SUPABASE_DB_HOST: str = os.getenv("SUPABASE_DB_HOST", "db.supabase.co")
    SUPABASE_DB_PORT: int = int(os.getenv("SUPABASE_DB_PORT", "5432"))
    SUPABASE_DB_NAME: str = os.getenv("SUPABASE_DB_NAME", "postgres")
    SUPABASE_DB_USER: str = os.getenv("SUPABASE_DB_USER", "postgres")
    SUPABASE_DB_PASSWORD: str = os.getenv("SUPABASE_DB_PASSWORD", "")

    @computed_field
    @property
    def SUPABASE_DB_URL(self) -> str:
        """Construct database URL from components"""
        return f"postgresql://{self.SUPABASE_DB_USER}:{self.SUPABASE_DB_PASSWORD}@{self.SUPABASE_DB_HOST}:{self.SUPABASE_DB_PORT}/{self.SUPABASE_DB_NAME}"

    # Storage Configuration
    STORAGE_PROVIDER: str = os.getenv("STORAGE_PROVIDER", "supabase")
    STORAGE_PATH: str = os.getenv("STORAGE_PATH", str(Path("/app/storage").resolve()))
    STORAGE_PUBLIC_URL: str = os.getenv("STORAGE_PUBLIC_URL", "http://localhost:8000/storage")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

    # Celery Configuration
    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = REDIS_URL
    TASK_QUEUE_MAX_RETRIES: int = 3
    TASK_QUEUE_RETRY_DELAY: int = 60  # seconds

    # AI Service Configuration
    AI_SERVICE_URL: str = "http://ai-service:8001"
    AI_SERVICE_KEY: Optional[str] = None

    # Security Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS Configuration
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000"]

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_METRICS_PORT: int = 9090

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"  # Allow extra fields from env file


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings() 