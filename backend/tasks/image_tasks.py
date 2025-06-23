from celery_app import celery
from supabase import create_client
import os
import requests
import logging
import time

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
MAKEIT3D_API_KEY = os.getenv("MAKEIT3D_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY or not MAKEIT3D_API_KEY:
    raise RuntimeError("Supabase or MakeIt3D credentials not set")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
logger = logging.getLogger("image_tasks")

@celery.task(name="tasks.image_tasks.process_image_task", bind=True, max_retries=3, default_retry_delay=10)
def process_image_task(self, image_id: str, image_url: str):
    try:
        logger.info(f"[Task] Sending image {image_id} to MakeIt3D...")

        task_id = f"{image_id}-bg-removal"

        # 1. Submit job to MakeIt3D
        submit = requests.post(
            "https://api.makeit3d.io/generate/remove-background",
            headers={
                "X-API-Key": MAKEIT3D_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "task_id": task_id,
                "provider": "stability",
                "input_image_asset_url": image_url,
                "output_format": "png"
            },
            timeout=30
        )

        if submit.status_code != 200:
            logger.warning(f"[Task] MakeIt3D submit error: {submit.status_code} - {submit.text}")
            supabase.table("images").update({
                "status": "error",
                "error_message": f"MakeIt3D API error: {submit.text}"
            }).eq("id", image_id).execute()
            return

        logger.info(f"[Task] Task submitted successfully: {task_id}")

        # 2. Poll for result
        max_attempts = 30
        attempt = 0
        output_url = None

        while attempt < max_attempts:
            time.sleep(2)
            status_res = requests.get(
                f"https://api.makeit3d.io/tasks/{task_id}/status",
                headers={"X-API-Key": MAKEIT3D_API_KEY}
            )

            if status_res.status_code != 200:
                logger.warning(f"[Task] Polling failed (try {attempt+1}): {status_res.text}")
                attempt += 1
                continue

            status_data = status_res.json()
            logger.info(f"[Task] Polling status: {status_data.get('status')}")

            if status_data.get("status") == "complete":
                output_url = status_data.get("asset_url")
                break
            elif status_data.get("status") == "failed":
                raise Exception(f"Processing failed: {status_data.get('error', 'Unknown')}")

            attempt += 1

        if not output_url:
            raise Exception("Timed out waiting for MakeIt3D result")

        # 3. Update Supabase
        supabase.table("images").update({
            "status": "processed",
            "processed_url": output_url
        }).eq("id", image_id).execute()

        logger.info(f"[Task] ✅ Image {image_id} processed successfully")

        return {"status": "done", "image_id": image_id, "output_url": output_url}

    except Exception as e:
        logger.error(f"[Task] Error processing image {image_id}: {e}")
        supabase.table("images").update({
            "status": "error",
            "error_message": str(e)
        }).eq("id", image_id).execute()
        raise self.retry(exc=e)
