from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List
from .base import TimestampedModel

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessingType(str, Enum):
    BACKGROUND_REMOVAL = "background_removal"
    OPTIMIZATION = "optimization"
    RESIZE = "resize"
    BULK = "bulk"

class ImageJob(TimestampedModel):
    id: str = Field(...)
    shop_id: str = Field(...)
    product_id: Optional[str] = None
    image_url: str = Field(...)
    status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    processing_type: List[ProcessingType] = Field(...)
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "job_123",
                "shop_id": "shop_123",
                "product_id": "prod_123",
                "image_url": "https://cdn.shopify.com/image.jpg",
                "status": "pending",
                "processing_type": ["background_removal", "optimization"],
                "result_url": None,
                "error_message": None,
                "metadata": {
                    "original_size": 1024000,
                    "processed_size": None
                }
            }
        } 