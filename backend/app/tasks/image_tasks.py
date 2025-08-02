import os
import requests
import uuid
from app.services.supabase_service import supabase
from app.logging_config import logger
from celery import shared_task

MAKEIT3D_API_KEY = os.getenv("MAKEIT3D_API_KEY")
MAKEIT3D_BASE_URL = "https://api.makeit3d.io"
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "makeit3d-public")

headers = {
    "X-API-Key": MAKEIT3D_API_KEY,
    "Content-Type": "application/json",
}


@shared_task
def submit_job_task(image_id: str, operation: str, image_url: str, shop: str):
    logger.info(f"Submitting job for image_id: {image_id}, operation: {operation}")

    endpoint = {
        "remove-background": "/generate/remove-background",
        "upscale": "/generate/upscale",
        "downscale": "/generate/downscale"
    }.get(operation)

    if not endpoint:
        logger.error(f"Invalid operation: {operation}")
        supabase.table("images").update({"status": "failed"}).eq("id", image_id).execute()
        return

    try:
        res = requests.post(f"{MAKEIT3D_BASE_URL}{endpoint}", json={"image_url": image_url}, headers=headers)
        res.raise_for_status()
        task_id = res.json().get("task_id")

        if not task_id:
            raise ValueError("task_id not found in response")

        supabase.table("images").update({
            "status": "processing",
            "external_task_id": task_id,
            "shop_folder": shop
        }).eq("id", image_id).execute()

        logger.info(f"✅ Job submitted for image {image_id}, task_id {task_id}")

    except Exception as e:
        logger.error(f"❌ Failed to submit job: {e}")
        supabase.table("images").update({"status": "failed"}).eq("id", image_id).execute()


@shared_task
def poll_all_processing_images():
    logger.info("🔄 Polling all processing images...")

    try:
        response = supabase.table("images").select("*").eq("status", "processing").execute()
        images = response.data or []

        for img in images:
            task_id = img.get("external_task_id")
            image_id = img.get("id")
            shop_folder = img.get("shop_folder")

            try:
                res = requests.get(f"{MAKEIT3D_BASE_URL}/tasks/{task_id}/status", headers=headers)
                res.raise_for_status()
                status_data = res.json()

                if status_data["status"] == "complete":
                    output_url = status_data.get("output_url")

                    if output_url:
                        try:
                            image_res = requests.get(output_url)
                            image_res.raise_for_status()

                            filename = f"{uuid.uuid4()}.png"
                            storage_path = f"{shop_folder}/processed/{filename}"

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
