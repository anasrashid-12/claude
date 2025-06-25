# backend/routers/webhook_router.py
from fastapi import APIRouter, Request, Header, HTTPException
from supabase import create_client
import os
import hmac
import hashlib
import base64
import logging

webhook_router = APIRouter()

# Environment Variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")

# Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
logger = logging.getLogger("uvicorn")


# 🔐 Verify Shopify Webhook HMAC
def verify_webhook(hmac_header: str, data: bytes) -> bool:
    hash_bytes = hmac.new(SHOPIFY_API_SECRET.encode(), data, hashlib.sha256).digest()
    expected_hmac = base64.b64encode(hash_bytes).decode()
    return hmac.compare_digest(hmac_header, expected_hmac)


# 🚫 App Uninstall Webhook Endpoint
@webhook_router.post("/webhooks/uninstall")
async def handle_uninstall(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None),
):
    try:
        body = await request.body()

        if not x_shopify_hmac_sha256 or not verify_webhook(x_shopify_hmac_sha256, body):
            logger.warning("[Webhook] Invalid uninstall webhook HMAC")
            raise HTTPException(status_code=403, detail="Invalid webhook signature")

        payload = await request.json()
        shop = payload.get("myshopify_domain")

        if not shop:
            raise HTTPException(status_code=400, detail="Missing shop domain in webhook payload")

        # 🗑️ Delete shop from `shops` table
        supabase.table("shops").delete().eq("shop", shop).execute()
        logger.info(f"[Webhook] Shop {shop} removed from 'shops' table")

        # 🗑️ Optionally delete all images related to the shop
        supabase.table("images").delete().eq("shop", shop).execute()
        logger.info(f"[Webhook] Images for shop {shop} removed from 'images' table")

        return {"success": True, "message": f"Shop {shop} removed successfully"}

    except Exception as e:
        logger.error(f"[Webhook] Error handling uninstall webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


__all__ = ["webhook_router"]
