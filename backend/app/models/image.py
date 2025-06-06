from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, HttpUrl

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessingType(str, Enum):
    BACKGROUND_REMOVAL = "background_removal"
    RESIZE = "resize"
    OPTIMIZE = "optimize"
    CUSTOM = "custom"

class ImageBase(BaseModel):
    store_id: int
    product_id: str
    image_id: str
    original_url: HttpUrl
    position: Optional[int] = None
    alt_text: Optional[str] = None

class ImageCreate(ImageBase):
    processing_types: List[ProcessingType]
    processing_options: Optional[Dict] = None

class ImageUpdate(BaseModel):
    processed_url: Optional[HttpUrl] = None
    status: Optional[ProcessingStatus] = None
    error_message: Optional[str] = None
    processing_options: Optional[Dict] = None

class Image(ImageBase):
    id: int
    created_at: datetime
    updated_at: datetime
    processed_url: Optional[HttpUrl] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    processing_types: List[ProcessingType]
    processing_options: Optional[Dict] = None
    error_message: Optional[str] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    task_id: Optional[str] = None
    version: int = 1
    metadata: Optional[Dict] = None

    class Config:
        from_attributes = True 