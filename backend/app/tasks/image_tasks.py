import os
import time
import requests
import uuid
from app.services.supabase_service import supabase
from app.logging_config import logger
from celery import shared_task

MAKEIT3D_API_KEY = os.getenv("MAKEIT3D_API_KEY")
MAKEIT3D_BASE_URL = "https://api.makeit3d.io"
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "makeit3d-public")

HEADERS = {
    "X-API-Key": MAKEIT3D_API_KEY,
    "Content-Type": "application/json",
}

@shared_task(queue="image_queue")
def submit_job_task(image_id: str, operation: str, image_path: str, shop: str):
    logger.info(f"🚀 Starting job for image_id: {image_id}, operation: {operation}")

    try:
        signed_url = None
        for attempt in range(10):
            signed_res = supabase.storage.from_(SUPABASE_BUCKET).create_signed_url(
                path=image_path, expires_in=60 * 60 * 24
            )
            signed_url = signed_res.get("signedURL")
            
            if signed_url:
                break

            logger.warning(f"🕐 Waiting for file {image_path} to be ready in Supabase... Attempt {attempt+1}/10")
            time.sleep(5)

        if not signed_url:
            raise FileNotFoundError(f"Uploaded file not found or signed URL failed: {image_path}")

        # ✅ File found, mark as queued
        supabase.table("images").update({"status": "queued"}).eq("id", image_id).execute()

        # Get signed URL for processing
        signed_res = supabase.storage.from_(SUPABASE_BUCKET).create_signed_url(
            path=image_path, expires_in=60 * 60 * 24 * 7
        )
        image_url = signed_res.get("signedURL")
        if not image_url:
            raise Exception("Signed URL generation failed")

        # ✅ Mark as processing
        supabase.table("images").update({"status": "processing"}).eq("id", image_id).execute()

    except Exception as sign_err:
        logger.error(f"❌ Pre-processing error: {sign_err}")
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

@shared_task(bind=True, max_retries=20, default_retry_delay=10)  # retry every 10s
def poll_all_processing_images(self):
    logger.info("🔄 Polling all images with status='processing'...")

    try:
        response = supabase.table("images").select("*").eq("status", "processing").execute()
        images = response.data or []

        if not images:
            logger.info("✅ No images left in processing. Polling complete.")
            return "done"

        logger.info(f"🧩 Found {len(images)} processing images. Polling each...")

        for img in images:
            task_id = img.get("task_id")
            image_id = img.get("id")
            shop = img.get("shop")
            poll_attempts = img.get("poll_attempts", 0)

            # If already tried 3 times, mark as failed
            if poll_attempts >= 3:
                logger.warning(f"⛔ Image {image_id} exceeded max retries. Marking as failed.")
                supabase.table("images").update({"status": "failed"}).eq("id", image_id).execute()
                continue

            try:
                res = requests.get(f"{MAKEIT3D_BASE_URL}/tasks/{task_id}/status", headers=HEADERS)
                res.raise_for_status()
                status_data = res.json()

                if status_data["status"] == "complete":
                    asset_url = status_data.get("asset_url")

                    if asset_url:
                        try:
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
                                raise Exception(f"Upload failed to Supabase storage: {upload_res.error.message}")

                            signed_res = supabase.storage.from_(SUPABASE_BUCKET).create_signed_url(
                                path=storage_path,
                                expires_in=60 * 60 * 24 * 7
                            )

                            signed_url = signed_res.get("signedURL")

                            supabase.table("images").update({
                                "status": "processed",
                                "processed_url": signed_url
                            }).eq("id", image_id).execute()

                            logger.info(f"✅ Image {image_id} processed and stored.")

                        except Exception as file_err:
                            logger.error(f"❌ Upload error for image {image_id}: {file_err}")
                            supabase.table("images").update({
                                "status": "failed",
                                "error_message": str(file_err)
                            }).eq("id", image_id).execute()

                elif status_data["status"] == "failed":
                    supabase.table("images").update({
                        "status": "failed",
                        "error_message": "Image failed during processing."
                    }).eq("id", image_id).execute()
                    logger.warning(f"⚠️ Image {image_id} failed during processing.")

                else:
                    # Still processing: increment poll_attempts
                    supabase.table("images").update({
                        "poll_attempts": poll_attempts + 1
                    }).eq("id", image_id).execute()
                    logger.info(f"⏳ Image {image_id} still processing. Attempt {poll_attempts + 1}/3.")

            except Exception as poll_error:
                logger.error(f"❌ Poll error for image {image_id}: {poll_error}")
                # Increment attempt on error too
                supabase.table("images").update({
                    "poll_attempts": poll_attempts + 1,
                    "error_message": str(poll_error)
                }).eq("id", image_id).execute()

        # 👇 Re-check after this cycle
        recheck = supabase.table("images").select("id").eq("status", "processing").execute()
        if recheck.data:
            logger.info("🔁 Still processing images found. Retrying in 10s...")
            raise self.retry()

        logger.info("✅ All processing complete. Polling task done.")
        return "done"

    except Exception as e:
        logger.error(f"❌ Unexpected polling error: {e}")
        raise self.retry(exc=e)
