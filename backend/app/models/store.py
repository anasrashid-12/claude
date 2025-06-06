from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl

class StoreBase(BaseModel):
    shop_domain: str
    access_token: Optional[str] = None
    is_active: bool = True

class StoreCreate(StoreBase):
    pass

class StoreUpdate(StoreBase):
    pass

class Store(StoreBase):
    id: int
    created_at: datetime
    updated_at: datetime
    installed_at: Optional[datetime] = None
    uninstalled_at: Optional[datetime] = None
    shop_name: Optional[str] = None
    shop_email: Optional[str] = None
    shop_plan: Optional[str] = None
    shop_owner: Optional[str] = None
    shop_country: Optional[str] = None
    shop_currency: Optional[str] = None
    shop_timezone: Optional[str] = None
    myshopify_domain: HttpUrl
    primary_locale: str = "en"
    plan_name: Optional[str] = None
    plan_display_name: Optional[str] = None
    api_version: str = "2024-01"

    class Config:
        from_attributes = True 