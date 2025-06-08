from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, HttpUrl, Field, UUID4
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from typing_extensions import TypedDict

from app.db.base_class import Base

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessingType(str, Enum):
    BACKGROUND_REMOVAL = "background_removal"
    RESIZE = "resize"
    OPTIMIZE = "optimize"
    REVERT = "revert"

class ImageMetadata(TypedDict):
    width: int
    height: int
    format: str
    size: int

class ProcessingSettings(TypedDict, total=False):
    quality: int
    format: str
    width: int
    height: int
    remove_background: bool

class ImageBase(BaseModel):
    """Base Image model"""
    product_id: UUID4
    shopify_image_id: str
    original_url: str
    current_url: str
    position: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None

    class Config:
        from_attributes = True

class ImageCreate(ImageBase):
    """Image creation model"""
    pass

class ImageUpdate(BaseModel):
    """Image update model"""
    current_url: Optional[str] = None
    position: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None

class ProcessingHistoryCreate(BaseModel):
    """Processing history creation model"""
    image_id: UUID4
    operation: ProcessingType
    status: ProcessingStatus = ProcessingStatus.PENDING
    settings: Optional[ProcessingSettings] = None
    backup_url: Optional[str] = None

class ProcessingHistory(ProcessingHistoryCreate):
    """Complete processing history model"""
    id: UUID4
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ImageVersion(BaseModel):
    """Image version model"""
    id: UUID4
    image_id: UUID4
    version_number: int
    storage_url: str
    created_at: datetime
    processing_history_id: Optional[UUID4] = None

    class Config:
        from_attributes = True

class Image(ImageBase):
    """Complete Image model"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    versions: List[ImageVersion] = Field(default_factory=list)
    processing_history: List[ProcessingHistory] = Field(default_factory=list)

    class Config:
        from_attributes = True 