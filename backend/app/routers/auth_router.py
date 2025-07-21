from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from supabase import create_client
import os
import httpx
import jwt
import time
import urllib.parse

# 🔐 Environment Variables
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL")
BACKEND_URL = os.getenv("BACKEND_URL")
SCOPES = os.getenv("SHOPIFY_SCOPES", "read_products,write_products")
JWT_SECRET = os.getenv("JWT_SECRET")

if not all([SHOPIFY_API_KEY, SHOPIFY_API_SECRET, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, FRONTEND_URL, BACKEND_URL]):
    raise RuntimeError("❌ Missing one or more required environment variables.")

REDIRECT_URI = f"{BACKEND_URL}/auth/callback"

# 🔗 Supabase Client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# 🚀 Router
auth_router = APIRouter()


# 🔑 JWT Token Generator
def create_jwt(shop: str):
    payload = {
        "shop": shop,
        "exp": int(time.time()) + 86400,  # 1 day expiry
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


# 🔔 Register Uninstall Webhook
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
        res = await client.post(url, headers=headers, json=payload)
        print("🔔 Uninstall webhook registered:", res.status_code, res.text)


# ✅ OAuth Install Route
@auth_router.get("/auth/install")
async def install(request: Request, shop: str = None, host: str = None):
    if not shop or not host:
        raise HTTPException(status_code=400, detail="Missing shop or host parameter")

    query = urllib.parse.urlencode({
        "client_id": SHOPIFY_API_KEY,
        "scope": SCOPES,
        "redirect_uri": REDIRECT_URI,
        "state": host,  # pass host to callback
    })

    install_url = f"https://{shop}/admin/oauth/authorize?{query}"
    print("🛠️ Install redirect to:", install_url)
    return RedirectResponse(install_url)


# ✅ OAuth Callback Route
@auth_router.get("/auth/callback")
async def auth_callback(request: Request):
    shop = request.query_params.get("shop")
    code = request.query_params.get("code")
    host = request.query_params.get("state")

    print("🔁 Callback received")
    print("🔧 shop:", shop)
    print("🔧 code:", code)
    print("🔧 host:", host)

    if not shop or not code or not host:
        raise HTTPException(status_code=400, detail="Missing shop, code, or host")

    # 🔑 Exchange code for access token
    token_url = f"https://{shop}/admin/oauth/access_token"
    payload = {
        "client_id": SHOPIFY_API_KEY,
        "client_secret": SHOPIFY_API_SECRET,
        "code": code,
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(token_url, json=payload)
        print("🔑 Token response:", res.status_code, res.text)
        res.raise_for_status()
        access_token = res.json().get("access_token")

    if not access_token:
        raise HTTPException(status_code=500, detail="Access token not received")

    # 📥 Save to Supabase
    print("💾 Saving shop to Supabase:", shop)
    supabase.table("shops").upsert(
        {
            "shop": shop,
            "access_token": access_token,
        },
        on_conflict=["shop"]
    ).execute()

    # 🔔 Register uninstall webhook
    await register_uninstall_webhook(shop, access_token)

    # 🔐 Create session JWT
    token = create_jwt(shop)

    # 🍪 Set cookies and redirect
    dashboard_url = f"{FRONTEND_URL}/dashboard?shop={shop}&host={host}&token={token}"
    print("🚀 Redirecting to frontend:", dashboard_url)

    response = RedirectResponse(url=dashboard_url)
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=True,
        samesite="None",
        max_age=86400,
        path="/",
    )
    response.set_cookie(
        key="host",
        value=host,
        httponly=False,
        secure=True,
        samesite="None",
        max_age=86400,
        path="/",
    )
    response.set_cookie(
        key="shop",
        value=shop,
        httponly=False,
        secure=True,
        samesite="None",
        max_age=86400,
        path="/",
    )

    return response
