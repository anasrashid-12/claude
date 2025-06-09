from typing import List, Union, Optional
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
import json
from functools import lru_cache

load_dotenv()

class Settings(BaseSettings):
    # Base Configuration
    PROJECT_NAME: str = "Shopify AI Image App"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Shopify Configuration
    SHOPIFY_API_KEY: str
    SHOPIFY_API_SECRET: str
    SHOPIFY_APP_URL: str
    SHOPIFY_SCOPES: str = "write_products,write_files,read_files"
    SHOPIFY_API_VERSION: str = "2024-01"  # Latest stable version

    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str

    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # AI Service Configuration
    AI_SERVICE_URL: str = "http://ai-service:8001"
    AI_SERVICE_KEY: Optional[str] = None

    # Security Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS Configuration
    BACKEND_CORS_ORIGINS: list = ["*"]  # In production, replace with actual origins

    # Storage Configuration
    STORAGE_PROVIDER: str = "supabase"  # Can be 'supabase' or 's3'
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB

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