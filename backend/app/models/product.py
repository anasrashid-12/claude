from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4

class ProductBase(BaseModel):
    """Base Product model"""
    store_id: UUID4
    shopify_product_id: str
    title: str
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    last_processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProductCreate(ProductBase):
    """Product creation model"""
    pass

class ProductUpdate(BaseModel):
    """Product update model"""
    title: Optional[str] = None
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    last_processed_at: Optional[datetime] = None

class Product(ProductBase):
    """Complete Product model"""
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 