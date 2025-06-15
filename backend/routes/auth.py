# backend/routers/auth_routes.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import requests, hashlib, hmac, base64, urllib.parse, os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

auth_router = APIRouter()

SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")
REDIRECT_URI = os.getenv("SHOPIFY_REDIRECT_URI")


def verify_hmac(params: dict, hmac_to_verify: str) -> bool:
    sorted_params = "&".join(
        f"{k}={','.join(v) if isinstance(v, list) else v}"
        for k, v in sorted(params.items())
        if k != "hmac"
    )
    digest = hmac.new(
        SHOPIFY_API_SECRET.encode("utf-8"),
        sorted_params.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(digest, hmac_to_verify)


@auth_router.get("/auth/callback")
async def auth_callback(request: Request):
    params = dict(request.query_params)
    hmac_param = params.get("hmac")

    if not verify_hmac(params, hmac_param):
        raise HTTPException(status_code=400, detail="HMAC validation failed")

    shop = params.get("shop")
    code = params.get("code")

    # Step 1: Exchange code for access token
    token_url = f"https://{shop}/admin/oauth/access_token"
    response = requests.post(token_url, json={
        "client_id": SHOPIFY_API_KEY,
        "client_secret": SHOPIFY_API_SECRET,
        "code": code
    })

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get access token")

    access_token = response.json().get("access_token")

    # Step 2: Save to Supabase
    supabase.table("shops").upsert({
        "shop": shop,
        "access_token": access_token
    }).execute()

    return RedirectResponse(url=f"{os.getenv('FRONTEND_URL')}/dashboard")
