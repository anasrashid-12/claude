from typing import List, AnyHttpUrl
from pydantic_settings import BaseSettings
from pydantic import validator
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Shopify AI Image Processor"
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    
    # CORS Settings
    CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Redis Settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_URL: str = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

    # Shopify Settings
    SHOPIFY_API_KEY: str = os.getenv("SHOPIFY_API_KEY", "")
    SHOPIFY_API_SECRET: str = os.getenv("SHOPIFY_API_SECRET", "")
    SHOPIFY_SCOPES: List[str] = [
        "read_products",
        "write_products",
        "read_files",
        "write_files"
    ]

    # JWT Settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Rate Limiting
    RATE_LIMIT_PER_SECOND: int = 10
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000

    # Image Processing
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif"]
    IMAGE_PROCESSING_TIMEOUT: int = 300  # 5 minutes

    # Storage Settings
    STORAGE_PROVIDER: str = os.getenv("STORAGE_PROVIDER", "local")  # local, s3, or r2
    STORAGE_BUCKET: str = os.getenv("STORAGE_BUCKET", "")
    STORAGE_ACCESS_KEY: str = os.getenv("STORAGE_ACCESS_KEY", "")
    STORAGE_SECRET_KEY: str = os.getenv("STORAGE_SECRET_KEY", "")
    STORAGE_REGION: str = os.getenv("STORAGE_REGION", "")

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 