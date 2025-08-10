from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from supabase import create_client
import jwt
import os
from app.services.supabase_service import get_shop_credits

me_router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

@me_router.get("/me")
async def get_me(request: Request):
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Missing session cookie")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        shop = payload.get("shop")
        if not shop:
            raise HTTPException(status_code=400, detail="Missing shop in token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Fetch shop record
    result = supabase.table("shops").select("*").eq("shop", shop).maybe_single().execute()
    shop_data = result.data or {}
    if not shop_data:
        raise HTTPException(status_code=404, detail="Shop not found")

    # Fetch credits
    try:
        credits = get_shop_credits(shop) or 0
    except Exception as e:
        print(f"[get_me] Error fetching credits: {e}")
        credits = 0

    return JSONResponse({
        "shop": shop,
        "status": "authenticated",
        "plan": shop_data.get("plan", "free"),
        "credits": credits
    })
