from fastapi import APIRouter, Request, Query
from fastapi.responses import RedirectResponse  
import urllib.parse

auth_router = APIRouter()

SHOPIFY_API_KEY = "39e28007c7d0d65a26cc66cef72fa7c2"
SCOPES = "read_products,write_products"
REDIRECT_URI = "https://6a8a-2400-adc1-47c-4e00-f584-ac49-1130-c0fb.ngrok-free.app/auth/callback"

@auth_router.get("/auth/install")
async def install(shop: str = Query(...)):
    if not shop:
        return {"error": "Missing shop parameter"}
    
    install_url = (
        f"https://{shop}/admin/oauth/authorize?"
        f"client_id={SHOPIFY_API_KEY}&scope={urllib.parse.quote(SCOPES)}&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&state=123456"
    )

    return RedirectResponse(install_url)
