# backend/services/supabase.py
import os
from supabase import create_client
import logging

logger = logging.getLogger("supabase_service")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing Supabase credentials in environment")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_shop_token(shop: str, access_token: str):
    try:
        response = supabase.table("shops").upsert({
            "shop": shop,
            "access_token": access_token
        }).execute()
        logger.info(f"[Supabase] Token saved for shop: {shop}")
        return response
    except Exception as e:
        logger.error(f"[Supabase] Failed to save token: {e}")
        raise
