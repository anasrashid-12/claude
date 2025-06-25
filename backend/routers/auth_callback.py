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

logger = logging.getLogger("auth_callback")


def create_jwt(shop: str):
    payload = {
        "shop": shop,
        "exp": int(time.time()) + 86400,  # 1 day expiry
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


async def register_uninstall_webhook(shop: str, access_token: str):
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
                logger.warning(f"[Webhook] Failed for {shop}: {res.status_code} {res.text}")
            else:
                logger.info(f"[Webhook] Registered for {shop}")
        except Exception as e:
            logger.error(f"[Webhook] Error for {shop}: {e}")


@auth_callback_router.get("/auth/callback")
async def auth_callback(request: Request):
    shop = request.query_params.get("shop")
    code = request.query_params.get("code")

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
            res.raise_for_status()
            access_token = res.json().get("access_token")
        except Exception as e:
            logger.error(f"[Auth] Token error for {shop}: {e}")
            raise HTTPException(status_code=500, detail="OAuth token exchange error")

    if not access_token:
        raise HTTPException(status_code=400, detail="Access token missing")

    try:
        supabase.table("shops").upsert({
            "shop": shop,
            "access_token": access_token,
        }).execute()
        logger.info(f"[Auth] Token saved for {shop}")
    except Exception as e:
        logger.error(f"[Supabase] Save error for {shop}: {e}")
        raise HTTPException(status_code=500, detail="Database error")

    await register_uninstall_webhook(shop, access_token)

    token = create_jwt(shop)

    response = RedirectResponse(url=f"{FRONTEND_URL}/dashboard")
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=True,
        samesite="None",
        max_age=86400,  # 1 day
    )
    return response


__all__ = ["auth_callback_router"]
