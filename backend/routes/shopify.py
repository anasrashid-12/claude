# backend/routes/shopify.py
from fastapi import APIRouter, Depends
from utils.auth import verify_jwt
from utils.shopify_api import get_products

router = APIRouter(prefix="/shopify", tags=["Shopify"])

@router.get("/products")
def fetch_products(user=Depends(verify_jwt)):
    return get_products(user['shop'])