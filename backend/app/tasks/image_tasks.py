import os
import time
import requests
import uuid
from pathlib import Path
from app.services.supabase_service import supabase
from app.logging_config import logger
from app.services.signed_url_util import get_signed_url
from celery import shared_task

MAKEIT3D_API_KEY = os.getenv("MAKEIT3D_API_KEY")
MAKEIT3D_BASE_URL = "https://api.makeit3d.io"
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "makeit3d-public")

HEADERS = {
    "X-API-Key": MAKEIT3D_API_KEY,
    "Content-Type": "application/json",
}

def wait_for_signed_url(path: str, retries: int = 10, delay: int = 5) -> str:
    for attempt in range(retries):
        try:
            return get_signed_url(path, expires_in=60 * 60 * 24)
        except Exception:
            logger.warning(f"🕐 Waiting for file {path} to be ready... Attempt {attempt+1}/{retries}")
            time.sleep(delay)
    raise FileNotFoundError(f"File not found or timed out waiting: {path}")


@shared_task(queue="image_queue")
def submit_job_task(image_id: str, operation: str, image_path: str, shop: str):
    logger.info(f"🚀 Starting job for image_id: {image_id}, operation: {operation}")

    try:
        # Wait until the file is ready in Supabase
        signed_url = wait_for_signed_url(image_path)

        # ✅ Mark as queued
        supabase.table("images").update({"status": "queued"}).eq("id", image_id).execute()

        # Longer expiry signed URL for processing
        image_url = get_signed_url(image_path)

        # ✅ Mark as processing
        supabase.table("images").update({"status": "processing"}).eq("id", image_id).execute()

    except Exception as err:
        logger.error(f"❌ Pre-processing error: {err}")
        supabase.table("images").update({"status": "error"}).eq("id", image_id).execute()
        return

    endpoint_map = {
        "remove-bg": "/generate/remove-background",
        "upscale": "/generate/upscale",
        "downscale": "/generate/downscale"
    }
    endpoint = endpoint_map.get(operation)
    if not endpoint:
        logger.error(f"❌ Invalid operation: {operation}")
        supabase.table("images").update({"status": "error"}).eq("id", image_id).execute()
        return

    task_id = f"{operation}-{uuid.uuid4()}"
    payload = {
        "task_id": task_id,
        "input_image_asset_url": image_url,
    }

    if operation in ["remove-bg", "upscale"]:
        payload.update({
            "provider": "stability",
            "output_format": "png"
        })
        if operation == "upscale":
            payload.update({
                "model": "fast",
                "prompt": "high quality detailed image"
            })

    elif operation == "downscale":
        payload.update({
            "max_size_mb": 2.0,
            "aspect_ratio_mode": "original",
            "output_format": "jpeg"
        })

    try:
        res = requests.post(f"{MAKEIT3D_BASE_URL}{endpoint}", json=payload, headers=HEADERS)
        res.raise_for_status()
        api_response = res.json()

        task_id = api_response.get("task_id")
        if not task_id:
            raise ValueError("No task_id returned from MakeIt3D API")

        supabase.table("images").update({
            "task_id": task_id
        }).eq("id", image_id).execute()

        logger.info(f"✅ Submitted to MakeIt3D: Image ID: {image_id}, Task ID: {task_id}")

    except Exception as e:
        logger.error(f"❌ Failed to submit job for image {image_id}: {e}")
        supabase.table("images").update({"status": "error"}).eq("id", image_id).execute()

    poll_all_processing_images.apply_async(countdown=10)


@shared_task(bind=True, max_retries=20, default_retry_delay=10)
def poll_all_processing_images(self):
    logger.info("🔄 Polling all images with status='processing'...")

    try:
        response = supabase.table("images").select("*").eq("status", "processing").execute()
        images = response.data or []

        if not images:
            logger.info("✅ No images left in processing.")
            return "done"

        for img in images:
            task_id = img.get("task_id")
            image_id = img.get("id")
            shop = img.get("shop")
            poll_attempts = img.get("poll_attempts", 0)

            if poll_attempts >= 3:
                logger.warning(f"⛔ Max retries exceeded for image {image_id}")
                supabase.table("images").update({
                    "status": "failed",
                    "error_message": "Max polling attempts reached"
                }).eq("id", image_id).execute()
                continue

            try:
                res = requests.get(f"{MAKEIT3D_BASE_URL}/tasks/{task_id}/status", headers=HEADERS)
                res.raise_for_status()
                status_data = res.json()

                if status_data["status"] == "complete":
                    asset_url = status_data.get("asset_url")
                    if not asset_url:
                        raise Exception("Missing asset_url in task result")

                    image_res = requests.get(asset_url)
                    image_res.raise_for_status()

                    filename = f"{uuid.uuid4()}.png"
                    storage_path = f"{shop}/processed/{filename}"

                    upload_res = supabase.storage.from_(SUPABASE_BUCKET).upload(
                        path=storage_path,
                        file=image_res.content,
                        file_options={"content-type": "image/png"},
                    )

                    if hasattr(upload_res, "error") and upload_res.error:
                        raise Exception(f"Upload failed: {upload_res.error.message}")

                    signed_url = get_signed_url(storage_path)

                    supabase.table("images").update({
                        "status": "processed",
                        "processed_path": storage_path,
                        "filename": Path(storage_path).name
                    }).eq("id", image_id).execute()

                    logger.info(f"✅ Image {image_id} processed successfully.")

                elif status_data["status"] == "failed":
                    logger.warning(f"⚠️ Image {image_id} failed during processing.")
                    supabase.table("images").update({
                        "status": "failed",
                        "error_message": "Image failed during processing."
                    }).eq("id", image_id).execute()

                else:
                    supabase.table("images").update({
                        "poll_attempts": poll_attempts + 1
                    }).eq("id", image_id).execute()
                    logger.info(f"⏳ Still processing: {image_id} (Attempt {poll_attempts + 1}/3)")

            except Exception as poll_error:
                logger.error(f"❌ Poll error for {image_id}: {poll_error}")
                supabase.table("images").update({
                    "poll_attempts": poll_attempts + 1,
                    "error_message": str(poll_error)
                }).eq("id", image_id).execute()

        # Retry if any still in processing
        remaining = supabase.table("images").select("id").eq("status", "processing").execute()
        if remaining.data:
            logger.info("🔁 Still processing images found. Retrying in 10s...")
            raise self.retry()

        logger.info("✅ All processing complete.")
        return "done"

    except Exception as e:
        logger.error(f"❌ Unexpected polling error: {e}")
        raise self.retry(exc=e)
