from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.models import Shop
from app.services.shop_service import ShopService
from app.api.deps import get_current_shop

router = APIRouter()

@router.post("/", response_model=Shop)
async def create_shop(
    shop: Shop,
    shop_service: ShopService = Depends()
):
    """Create a new shop"""
    try:
        return await shop_service.create_shop(shop)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/current", response_model=Shop)
async def get_current_shop(
    shop: Shop = Depends(get_current_shop),
    shop_service: ShopService = Depends()
):
    """Get current shop details"""
    return shop

@router.put("/current", response_model=Shop)
async def update_shop(
    update_data: dict,
    shop: Shop = Depends(get_current_shop),
    shop_service: ShopService = Depends()
):
    """Update current shop settings"""
    try:
        return await shop_service.update_shop(shop.id, update_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/current/settings", response_model=dict)
async def get_shop_settings(
    shop: Shop = Depends(get_current_shop),
    shop_service: ShopService = Depends()
):
    """Get current shop settings"""
    return shop.settings

@router.put("/current/settings", response_model=dict)
async def update_shop_settings(
    settings: dict,
    shop: Shop = Depends(get_current_shop),
    shop_service: ShopService = Depends()
):
    """Update shop settings"""
    try:
        updated_shop = await shop_service.update_shop(shop.id, {"settings": settings})
        return updated_shop.settings
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 