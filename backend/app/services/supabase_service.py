import os
import logging
from supabase import create_client

logger = logging.getLogger("supabase_service")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("❌ Missing Supabase credentials in environment variables")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def save_shop_token(shop: str, access_token: str):
    """
    Upsert a Shopify shop and its access token into the `shops` table.
    """
    try:
        logger.info(f"[Supabase] 🔄 Upserting token for {shop}")
        response = supabase.table("shops").upsert(
            {"shop": shop, "access_token": access_token},
            on_conflict="shop"
        ).execute()
        logger.info(f"[Supabase] ✅ Token saved for {shop}")
        return response.data
    except Exception as e:
        logger.exception(f"[Supabase] ❌ Failed to save token for {shop}: {e}")
        raise
