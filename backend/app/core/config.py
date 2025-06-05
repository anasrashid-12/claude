from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Shopify AI Image Processing"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend development
        "https://admin.shopify.com",  # Shopify admin
    ]
    
    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Celery Settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # R2 Settings
    R2_ENDPOINT: str
    R2_ACCESS_KEY_ID: str
    R2_SECRET_ACCESS_KEY: str
    R2_BUCKET_NAME: str
    
    # Supabase Settings
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Image Processing
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    SUPPORTED_FORMATS: List[str] = ["jpg", "jpeg", "png", "webp"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 