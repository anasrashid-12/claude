from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field, UUID4, HttpUrl

class StoreBase(BaseModel):
    """Base Store model"""
    shop_domain: str
    access_token: Optional[str] = None
    is_active: bool = True
    plan_type: Optional[str] = None
    api_usage_count: int = 0
    last_sync_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class StoreCreate(StoreBase):
    """Store creation model"""
    pass

class StoreUpdate(BaseModel):
    """Store update model"""
    access_token: Optional[str] = None
    is_active: Optional[bool] = None
    plan_type: Optional[str] = None
    api_usage_count: Optional[int] = None
    last_sync_at: Optional[datetime] = None

class StoreSettings(BaseModel):
    """Store settings model"""
    id: UUID4
    store_id: UUID4
    default_image_settings: Dict = Field(default_factory=dict)
    auto_process_new_images: bool = False
    notification_email: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Store(StoreBase):
    """Complete Store model"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    settings: Optional[StoreSettings] = None

    class Config:
        from_attributes = True 