# backend/routers/auth_callback.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from supabase import create_client
from urllib.parse import urlencode
import jwt
import os
import httpx
import time
import logging

auth_callback_router = APIRouter()

# Environment variables
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
JWT_SECRET = os.getenv("JWT_SECRET", "maxflow_secret")

# Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Logger
logger = logging.getLogger("uvicorn")

# JWT helper
def create_jwt(shop: str):
    payload = {
        "shop": shop,
        "exp": int(time.time()) + 60 * 60 * 24,  # Expires in 1 day
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# Webhook registration helper
async def register_app_uninstall_webhook(shop: str, access_token: str):
    url = f"https://{shop}/admin/api/2023-10/webhooks.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json",
    }
    payload = {
        "webhook": {
            "topic": "app/uninstalled",
            "address": f"{BACKEND_URL}/webhooks/uninstall",
            "format": "json",
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(url, headers=headers, json=payload)
            if res.status_code != 201:
                logger.warning(f"[Webhook] Failed to register: {res.status_code} - {res.text}")
            else:
                logger.info(f"[Webhook] Uninstall webhook registered for shop: {shop}")
        except Exception as e:
            logger.error(f"[Webhook] Registration error for shop {shop}: {e}")

# OAuth Callback Route
@auth_callback_router.get("/callback")
async def auth_callback(request: Request):
    params = dict(request.query_params)
    shop = params.get("shop")
    code = params.get("code")

    if not shop or not code:
        raise HTTPException(status_code=400, detail="Missing shop or code")

    token_url = f"https://{shop}/admin/oauth/access_token"
    payload = {
        "client_id": SHOPIFY_API_KEY,
        "client_secret": SHOPIFY_API_SECRET,
        "code": code,
    }

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(token_url, json=payload)
            if res.status_code != 200:
                raise HTTPException(status_code=400, detail="Token exchange failed")
            access_token = res.json().get("access_token")
        except Exception as e:
            logger.error(f"[Auth] Token exchange failed for {shop}: {e}")
            raise HTTPException(status_code=500, detail="OAuth token exchange error")

    if not access_token:
        raise HTTPException(status_code=400, detail="Missing access token")

    # Save or update shop in Supabase
    try:
        existing = supabase.table("shops").select("id").eq("shop", shop).execute()
        if existing.data:
            supabase.table("shops").update({"access_token": access_token}).eq("shop", shop).execute()
        else:
            supabase.table("shops").insert({"shop": shop, "access_token": access_token}).execute()
        logger.info(f"[Auth] Access token saved for shop: {shop}")
    except Exception as e:
        logger.error(f"[Supabase] Failed to save access token: {e}")
        raise HTTPException(status_code=500, detail="Failed to store access token")

    # Register uninstall webhook
    await register_app_uninstall_webhook(shop, access_token)

    # Generate secure session token
    token = create_jwt(shop)

    # Redirect with secure cookie
    response = RedirectResponse(url=f"{FRONTEND_URL}/dashboard")
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,       # stays True for security
        secure=True,         # Must be True for cross-origin + SameSite=None
        samesite="None",     # Required for cross-origin requests
        max_age=86400,
    )

    return response

# This must be at the bottom
__all__ = ["auth_callback_router"]
