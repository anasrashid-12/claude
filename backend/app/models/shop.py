from pydantic import BaseModel, Field
from typing import Optional
from .base import TimestampedModel

class Shop(TimestampedModel):
    id: str = Field(...)
    shop_url: str = Field(...)
    access_token: str = Field(...)
    shop_name: str = Field(...)
    email: Optional[str] = None
    plan_name: Optional[str] = None
    is_active: bool = Field(default=True)
    processing_enabled: bool = Field(default=True)
    settings: dict = Field(default_factory=dict)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123",
                "shop_url": "my-store.myshopify.com",
                "access_token": "shpat_123...",
                "shop_name": "My Store",
                "email": "owner@example.com",
                "plan_name": "basic",
                "is_active": True,
                "processing_enabled": True,
                "settings": {
                    "default_background_removal": True,
                    "auto_optimize": True
                }
            }
        } 