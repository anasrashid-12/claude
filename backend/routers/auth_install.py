# backend/routers/auth_install.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import os
import urllib.parse

auth_install_router = APIRouter()

SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SCOPES = os.getenv("SHOPIFY_SCOPES", "read_products,write_products")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
REDIRECT_URI = f"{BACKEND_URL}/auth/callback"

@auth_install_router.get("/install")
async def install(request: Request, shop: str = None):
    if not shop:
        raise HTTPException(status_code=400, detail="Missing shop parameter")
    
    # Prepare the Shopify OAuth URL
    query = urllib.parse.urlencode({
        "client_id": SHOPIFY_API_KEY,
        "scope": SCOPES,
        "redirect_uri": REDIRECT_URI,
    })
    
    redirect_url = f"https://{shop}/admin/oauth/authorize?{query}"
    return RedirectResponse(url=redirect_url)

__all__ = ["auth_install_router"]