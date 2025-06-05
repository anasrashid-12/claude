from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

class StoreAuth(BaseModel):
    shop: str
    access_token: str

class ProductSync(BaseModel):
    shop: str
    sync_all: bool = True
    product_ids: Optional[List[str]] = None

class ImageProcess(BaseModel):
    image_id: str
    operation: str
    settings: Optional[dict] = None

class WebhookPayload(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    body_html: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    handle: str
    status: str
    images: List[dict] 