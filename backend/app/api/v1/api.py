from fastapi import APIRouter

from app.api.v1.endpoints import images, shopify, health, auth

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(shopify.router, prefix="/shopify", tags=["shopify"]) 