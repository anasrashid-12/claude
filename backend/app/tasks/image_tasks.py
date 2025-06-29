from app.celery_app import celery_app
from supabase import create_client
import os
import requests
import logging
import time

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
MAKEIT3D_API_KEY = os.getenv("MAKEIT3D_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
logger = logging.getLogger("image_tasks")


@celery_app.task(bind=True, max_retries=3)
def process_image_task(self, image_id: str, makeit3d_url: str):
    try:
        task_id = f"{image_id}-bg-removal"

        submit = requests.post(
            "https://api.makeit3d.io/generate/remove-background",
            headers={"X-API-Key": MAKEIT3D_API_KEY, "Content-Type": "application/json"},
            json={
                "task_id": task_id,
                "provider": "stability",
                "input_image_asset_url": makeit3d_url,
                "output_format": "png"
            },
            timeout=30
        )

        if submit.status_code != 200:
            raise Exception(f"Submit error: {submit.text}")

        attempt = 0
        output_url = None
        while attempt < 30:
            time.sleep(3)
            status = requests.get(
                f"https://api.makeit3d.io/tasks/{task_id}/status",
                headers={"X-API-Key": MAKEIT3D_API_KEY},
            )
            data = status.json()

            if data.get("status") == "complete":
                output_url = data.get("asset_url")
                break
            elif data.get("status") == "failed":
                raise Exception(f"Processing failed: {data.get('error')}")
            attempt += 1

        if not output_url:
            raise Exception("❌ Timeout waiting for processing result")

        supabase.table("images").update({
            "status": "processed",
            "processed_url": output_url
        }).eq("id", image_id).execute()

        logger.info(f"[Task] ✅ Image {image_id} processed")
        return {
            "status": "done",
            "output_url": output_url,
            "image_id": image_id
        }

    except Exception as e:
        supabase.table("images").update({
            "status": "error",
            "error_message": str(e)
        }).eq("id", image_id).execute()

        logger.error(f"[Task] ❌ Error processing {image_id}: {e}")
        raise self.retry(exc=e)
