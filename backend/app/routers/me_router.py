from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from supabase import create_client
import jwt
import os

me_router = APIRouter()

# 🔑 Environment Variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")

# 🔗 Supabase Client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


@me_router.get("/me")
async def get_me(request: Request):
    # ✅ Try Authorization header first
    auth_header = request.headers.get("Authorization")
    token = None

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split("Bearer ")[1]
    
    # ✅ Fallback: check cookie
    if not token:
        token = request.cookies.get("session")

    if not token:
        raise HTTPException(status_code=401, detail="No session token found")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        shop = payload.get("shop")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid session token")

    if not shop:
        raise HTTPException(status_code=400, detail="Shop missing in token")

    # ✅ Fetch shop info from Supabase
    response = supabase.table("shops").select("*").eq("shop", shop).maybe_single().execute()
    shop_data = response.data

    if shop_data is None:
        raise HTTPException(status_code=404, detail="Shop not found")

    return JSONResponse({
        "shop": shop,
        "status": "authenticated",
        "plan": shop_data.get("plan", "free")
    })
