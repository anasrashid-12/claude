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
        task_id = f"{image_id}-remove-bg"
        logger.info(f"[Task] Submitting image {image_id} to MakeIt3D")

        # Step 1: Submit image for background removal
        response = requests.post(
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
            timeout=20
        )

        if response.status_code != 200:
            raise Exception(f"MakeIt3D API error: {response.status_code} - {response.text}")

        logger.info(f"[Task] Job submitted. Polling task_id={task_id}")

        # Step 2: Poll status
        poll_url = f"https://api.makeit3d.io/tasks/{task_id}/status"
        for attempt in range(40):  # max ~80s
            status_resp = requests.get(
                poll_url,
                headers={"X-API-Key": MAKEIT3D_API_KEY},
                timeout=10
            )
            status_data = status_resp.json()
            status = status_data.get("status")
            logger.info(f"[Task] Poll attempt {attempt}: {status}")

            if status == "complete":
                asset_url = status_data.get("asset_url")
                if not asset_url:
                    raise Exception("Processing complete, but no asset_url returned")

                supabase.table("images").update({
                    "status": "processed",
                    "processed_url": asset_url
                }).eq("id", image_id).execute()

                logger.info(f"[Task] Success: Image {image_id} processed")
                return {"status": "done", "image_id": image_id}

            if status == "failed":
                raise Exception(f"MakeIt3D task failed for {image_id}")

            time.sleep(2)

        raise Exception("MakeIt3D processing timed out")

    except Exception as e:
        logger.error(f"[Task] Error processing image {image_id}: {e}")
        supabase.table("images").update({
            "status": "error",
            "error_message": str(e)
        }).eq("id", image_id).execute()
        raise self.retry(exc=e)
