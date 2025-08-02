from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from supabase import create_client
import os, httpx, jwt, time, urllib.parse

# ──────────────────────🔐 Environment Variables ──────────────────────
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL")  # e.g., https://your-frontend.com
BACKEND_URL = os.getenv("BACKEND_URL")    # e.g., https://your-backend.com
SCOPES = os.getenv("SHOPIFY_SCOPES", "read_products,write_products")
JWT_SECRET = os.getenv("JWT_SECRET")

if not all([SHOPIFY_API_KEY, SHOPIFY_API_SECRET, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, FRONTEND_URL, BACKEND_URL]):
    raise RuntimeError("❌ Missing required environment variables.")

# ──────────────────────📦 Setup ──────────────────────
REDIRECT_URI = f"{BACKEND_URL}/auth/callback"
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
auth_router = APIRouter()


# ──────────────────────🔑 JWT Token ──────────────────────
def create_jwt(shop: str):
    return jwt.encode({
        "sub": shop,             # 👈 Required for Supabase auth.uid()
        "shop": shop,            # 👈 Used in RLS policies
        "exp": int(time.time()) + 86400,
    }, JWT_SECRET, algorithm="HS256")


# ──────────────────────🔔 Register Uninstall Webhook ──────────────────────
async def register_uninstall_webhook(shop: str, access_token: str):
    try:
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
            res.raise_for_status()
            print("✅ Webhook registered:", res.status_code)
    except Exception as e:
        print("❌ Webhook registration failed:", str(e))


# ──────────────────────🔁 Shopify OAuth Install ──────────────────────
@auth_router.get("/auth/install")
async def install(request: Request, shop: str = None, host: str = None):
    if not shop or not host:
        raise HTTPException(status_code=400, detail="Missing shop or host")

    # Redirect to frontend so we can break out of iframe
    return RedirectResponse(f"{FRONTEND_URL}/auth/toplevel?shop={shop}&host={host}")

@auth_router.get("/auth/oauth")
async def oauth(request: Request, shop: str = None, host: str = None):
    if not shop or not host:
        raise HTTPException(status_code=400, detail="Missing shop or host")

    query = urllib.parse.urlencode({
        "client_id": SHOPIFY_API_KEY,
        "scope": SCOPES,
        "redirect_uri": REDIRECT_URI,
        "state": host,
    })

    return RedirectResponse(f"https://{shop}/admin/oauth/authorize?{query}")

# ──────────────────────🔁 Shopify OAuth Callback ──────────────────────
@auth_router.get("/auth/callback")
async def auth_callback(request: Request):
    shop = request.query_params.get("shop")
    code = request.query_params.get("code")
    host = request.query_params.get("state")

    if not shop or not code or not host:
        raise HTTPException(status_code=400, detail="Missing callback parameters")

    try:
        # 🔐 Exchange code for access token
        token_url = f"https://{shop}/admin/oauth/access_token"
        payload = {
            "client_id": SHOPIFY_API_KEY,
            "client_secret": SHOPIFY_API_SECRET,
            "code": code,
        }

        async with httpx.AsyncClient() as client:
            res = await client.post(token_url, json=payload)
            res.raise_for_status()
            data = res.json()
            access_token = data.get("access_token")

        if not access_token:
            raise HTTPException(status_code=500, detail="Access token not received")

        # 💾 Save to Supabase
        supabase.table("shops").upsert({
            "shop": shop,
            "access_token": access_token,
        }, on_conflict=["shop"]).execute()

        # 🔔 Register uninstall webhook
        await register_uninstall_webhook(shop, access_token)

        # 🎫 Create session token
        jwt_token = create_jwt(shop)

        # 🚀 Redirect to frontend with secure cookies
        response = RedirectResponse(f"{FRONTEND_URL}/dashboard")

        # 🧁 Secure session cookie
        response.set_cookie(
            key="session",
            value=jwt_token,
            httponly=True,
            secure=True,
            samesite="None",
            max_age=86400,
            path="/",
        )

        # 🍪 Readable cookies (not httponly)
        response.set_cookie(
            key="shop",
            value=shop,
            secure=True,
            samesite="None",
            max_age=86400,
            path="/",
        )
        response.set_cookie(
            key="host",
            value=host,
            secure=True,
            samesite="None",
            max_age=86400,
            path="/",
        )

        return response

    except httpx.HTTPStatusError as e:
        print("❌ Shopify token exchange failed:", e.response.text)
        raise HTTPException(status_code=500, detail="Shopify auth failed")
    except Exception as e:
        print("❌ Unexpected error during OAuth callback:", str(e))
        raise HTTPException(status_code=500, detail="OAuth processing error")
