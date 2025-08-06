import os
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
def submit_job_task(image_id: str, operation: str, image_url: str, shop: str):
    logger.info(f"🚀 Submitting job for image_id: {image_id}, operation: {operation}")

    endpoint_map = {
        "remove-bg": "/generate/remove-background",
        "upscale": "/generate/upscale",
        "downscale": "/generate/downscale"
    }

    endpoint = endpoint_map.get(operation)
    if not endpoint:
        logger.error(f"❌ Invalid operation: {operation}")
        supabase.table("images").update({"status": "failed"}).eq("id", image_id).execute()
        return

    task_id = f"{operation}-{uuid.uuid4()}"
    payload = {
        "task_id": task_id,
        "input_image_asset_url": image_url,
    }

    if operation in ["remove-bg", "upscale"]:
        payload["provider"] = "stability"
        payload["output_format"] = "png"

        if operation == "upscale":
            payload["model"] = "fast"
            payload["prompt"] = "high quality detailed image"

    if operation == "downscale":
        payload["max_size_mb"] = 2.0
        payload["aspect_ratio_mode"] = "original"
        payload["output_format"] = "jpeg"

    try:
        res = requests.post(f"{MAKEIT3D_BASE_URL}{endpoint}", json=payload, headers=HEADERS)
        res.raise_for_status()
        api_response = res.json()
        task_id = api_response.get("task_id")

        if not task_id:
            raise ValueError("No task_id returned in response.")

        supabase.table("images").update({
            "status": "processing",
            "task_id": task_id
        }).eq("id", image_id).execute()

        logger.info(f"✅ Job submitted successfully. Image ID: {image_id}, Task ID: {task_id}")

    except Exception as e:
        logger.error(f"❌ Failed to submit job for image {image_id}: {e}")
        supabase.table("images").update({"status": "failed"}).eq("id", image_id).execute()


@shared_task
def poll_all_processing_images():
    logger.info("🔄 Polling all processing images...")

    try:
        response = supabase.table("images").select("*").eq("status", "processing").execute()
        images = response.data or []

        for img in images:
            task_id = img.get("task_id")
            image_id = img.get("id")
            shop = img.get("shop")

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

                            if upload_res.get("error"):
                                raise Exception(upload_res["error"]["message"])

                            signed_res = supabase.storage.from_(SUPABASE_BUCKET).create_signed_url(
                                path=storage_path,
                                expires_in=60 * 60 * 24 * 7
                            )

                            signed_url = signed_res.get("signedURL")

                            supabase.table("images").update({
                                "status": "completed",
                                "processed_url": signed_url
                            }).eq("id", image_id).execute()

                            logger.info(f"✅ Image {image_id} processed and saved to: {storage_path}")

                        except Exception as file_err:
                            logger.error(f"❌ Upload error for image {image_id}: {file_err}")
                            supabase.table("images").update({"status": "failed"}).eq("id", image_id).execute()

                elif status_data["status"] == "failed":
                    supabase.table("images").update({"status": "failed"}).eq("id", image_id).execute()
                    logger.warning(f"⚠️ Image {image_id} processing failed.")

            except Exception as poll_error:
                logger.error(f"❌ Polling failed for image {image_id}: {poll_error}")

    except Exception as fetch_error:
        logger.error(f"❌ Failed to fetch processing images: {fetch_error}")
