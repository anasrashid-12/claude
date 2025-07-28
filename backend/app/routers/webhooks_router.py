from fastapi import APIRouter, Request, HTTPException
from app.services.supabase_service import supabase
from app.logging_config import logger
import hmac
import hashlib
import base64
import os

webhook_router = APIRouter()
SHOPIFY_WEBHOOK_SECRET = os.getenv("SHOPIFY_API_SECRET")

def verify_webhook_hmac(body: bytes, hmac_header: str) -> bool:
    digest = hmac.new(SHOPIFY_WEBHOOK_SECRET.encode('utf-8'), body, hashlib.sha256).digest()
    calculated_hmac = base64.b64encode(digest).decode()
    return hmac.compare_digest(calculated_hmac, hmac_header)

@webhook_router.post("/webhooks/uninstall")
async def handle_uninstall(request: Request):
    try:
        body = await request.body()
        hmac_header = request.headers.get("X-Shopify-Hmac-Sha256")

        if not verify_webhook_hmac(body, hmac_header):
            logger.warning("[Webhook] Invalid HMAC in uninstall webhook")
            raise HTTPException(status_code=401, detail="Invalid HMAC")

        payload = await request.json()
        shop = payload.get("myshopify_domain")
        logger.info(f"[Webhook] Received uninstall webhook from {shop}")

        # 1. Delete all images from DB
        db_delete_response = supabase.table("images").delete().eq("shop", shop).execute()
        logger.info(f"[Webhook] Deleted {len(db_delete_response.data)} image records from DB for shop {shop}")

        # 2. Delete all files from Supabase Storage
        await delete_images_from_storage(shop)

        # 3. Delete shop record from DB
        shop_delete_response = supabase.table("shops").delete().eq("shop", shop).execute()
        logger.info(f"[Webhook] Deleted shop record for {shop}")

        return {"message": "Uninstall cleanup completed"}

    except Exception as e:
        logger.error(f"[Webhook] Error handling uninstall webhook: {e}")
        raise HTTPException(status_code=500, detail="Uninstall webhook failed")


async def delete_images_from_storage(shop: str):
    try:
        bucket = "makeit3d-public"
        list_response = supabase.storage.from_(bucket).list(path=shop)
        files = list_response.get("data", [])

        if not files:
            logger.info(f"[Storage] No files found for shop {shop}")
            return

        file_paths = [f"{shop}/{file['name']}" for file in files]
        delete_response = supabase.storage.from_(bucket).remove(file_paths)

        if delete_response.get("error"):
            logger.error(f"[Storage] Failed to delete files: {delete_response['error']}")
        else:
            logger.info(f"[Storage] Deleted {len(file_paths)} files for shop {shop}")

    except Exception as e:
        logger.error(f"[Storage] Error deleting files from storage: {e}")
