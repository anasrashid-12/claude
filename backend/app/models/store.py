from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field, UUID4, HttpUrl

class Store(BaseModel):
    id: Optional[UUID4] = None
    shop_domain: str
    access_token: str
    shop_name: str
    email: str
    country: str
    currency: str
    status: str  # 'active', 'inactive', 'suspended'
    webhook_url: Optional[str] = None
    subscription_status: Optional[str] = None  # 'trial', 'active', 'cancelled'
    trial_ends_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class StoreCreate(BaseModel):
    shop_domain: str
    access_token: str
    shop_name: str
    email: str
    country: str = ""
    currency: str = "USD"
    status: str = "active"

class StoreUpdate(BaseModel):
    shop_name: Optional[str] = None
    email: Optional[str] = None
    country: Optional[str] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    webhook_url: Optional[str] = None
    subscription_status: Optional[str] = None
    trial_ends_at: Optional[datetime] = None

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