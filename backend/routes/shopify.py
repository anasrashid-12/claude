# backend/routes/shopify.py
from fastapi import APIRouter, Depends
from utils.auth import verify_jwt
from utils.shopify_api import get_products

router = APIRouter(prefix="/shopify", tags=["Shopify"])

@router.get("/products")
def fetch_products(user=Depends(verify_jwt)):
    return get_products(user['shop'])

shopify_router = APIRouter()

@shopify_router.get("/shopify")
async def shopify_root():
    return {"message": "Shopify route working"}