from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field, UUID4, HttpUrl
from uuid import UUID

class StoreBase(BaseModel):
    """Base Store model"""
    shop_domain: str = Field(..., description="The Shopify store domain")
    access_token: Optional[str] = Field(None, description="The Shopify access token")
    installed_at: Optional[datetime] = Field(None, description="When the app was installed")
    uninstalled_at: Optional[datetime] = Field(None, description="When the app was uninstalled")

class StoreCreate(StoreBase):
    """Store creation model"""
    pass

class StoreUpdate(BaseModel):
    """Store update model"""
    access_token: Optional[str] = None
    uninstalled_at: Optional[datetime] = None

class Store(StoreBase):
    """Complete Store model"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

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