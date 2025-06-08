from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class ImageBase(BaseModel):
    product_id: str
    original_url: str
    processing_options: Optional[Dict] = None
    auth_user_id: Optional[str] = None

class ImageCreate(ImageBase):
    pass

class ImageUpdate(BaseModel):
    processed_url: Optional[str] = None
    status: Optional[str] = None
    processing_options: Optional[Dict] = None

class ImageResponse(ImageBase):
    id: str
    processed_url: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 