from fastapi import APIRouter, Request, HTTPException
from app.services.supabase_service import supabase
from app.logging_config import logger
import logging
import hmac
import hashlib
import base64
import os
from app.tasks.image_tasks import submit_job_task

webhook_router = APIRouter()
SHOPIFY_WEBHOOK_SECRET = os.getenv("SHOPIFY_API_SECRET")

def verify_webhook_hmac(body: bytes, hmac_header: str) -> bool:
    """
    Verifies the HMAC from Shopify webhook header.
    """
    digest = hmac.new(SHOPIFY_WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256).digest()
    calculated_hmac = base64.b64encode(digest).decode()
    return hmac.compare_digest(calculated_hmac, hmac_header or "")

@webhook_router.post("/webhooks/uninstall")
async def handle_uninstall(request: Request):
    """
    Shopify uninstall webhook handler:
    - Verifies HMAC
    - Deletes all shop-related files from Supabase storage
    - Removes shop and image records from Supabase DB
    """
    try:
        body = await request.body()
        hmac_header = request.headers.get("X-Shopify-Hmac-Sha256")

        if not verify_webhook_hmac(body, hmac_header):
            logger.warning("[Webhook] Invalid HMAC in uninstall webhook")
            raise HTTPException(status_code=401, detail="Invalid HMAC")

        payload = await request.json()
        shop = payload.get("myshopify_domain")

        if not shop:
            raise HTTPException(status_code=400, detail="Missing shop domain in webhook payload")

        logger.info(f"[Webhook] 🔔 Received uninstall webhook from {shop}")

        # Delete image files from Supabase Storage
        await delete_images_from_storage(shop)

        # Delete image records from Supabase DB
        img_res = supabase.table("images").delete().eq("shop", shop).execute()
        logger.info(f"[Webhook] 🗑️ Deleted {len(img_res.data)} image records from DB")

        # Delete shop record
        shop_res = supabase.table("shops").delete().eq("shop", shop).execute()
        logger.info(f"[Webhook] 🧹 Deleted shop record for {shop}")

        return {"message": f"Uninstall cleanup completed for {shop}"}

    except Exception as e:
        logger.error(f"[Webhook] ❌ Error handling uninstall webhook: {e}")
        raise HTTPException(status_code=500, detail="Uninstall webhook failed")

async def delete_images_from_storage(shop: str):
    """
    Deletes all images in Supabase Storage for the given shop.
    """
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
            logger.error(f"[Storage] ❌ Failed to delete files: {delete_response['error']}")
        else:
            logger.info(f"[Storage] ✅ Deleted {len(file_paths)} files for shop {shop}")

    except Exception as e:
        logger.error(f"[Storage] ⚠️ Error deleting files from storage: {e}")

@webhook_router.post("/webhook/image-upload")
async def handle_image_upload_webhook(request: Request):
    payload = await request.json()
    logging.info(f"📦 Received webhook payload: {payload}")

    image_id = payload.get("record", {}).get("id")
    if not image_id:
        return {"status": "missing image_id"}

    try:
        # Fetch image details from Supabase
        image_res = supabase.table("images").select("*").eq("id", image_id).single().execute()
        image = image_res.data
        if not image:
            return {"status": "image not found"}

        submit_job_task.delay(
            image_id=image["id"],
            operation=image["operation"],
            image_path=image["original_path"],
            shop=image["shop"]
        )

        logging.info(f"🚀 Celery job queued for image_id={image_id}")
        return {"status": "queued", "image_id": image_id}

    except Exception as e:
        logging.error(f"❌ Webhook processing failed: {e}")
        return {"status": "error", "error": str(e)}