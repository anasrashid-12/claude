from celery_app import celery
from supabase import create_client
import os
import requests
import logging

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
MAKEIT3D_API_KEY = os.getenv("MAKEIT3D_API_KEY")  # Set this in your .env

if not SUPABASE_URL or not SUPABASE_KEY or not MAKEIT3D_API_KEY:
    raise RuntimeError("Supabase or MakeIt3D credentials not set")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
logger = logging.getLogger("image_tasks")

@celery.task(name="process_image_task", bind=True, max_retries=3, default_retry_delay=10)
def process_image_task(self, image_id: str, image_url: str):
    try:
        logger.info(f"[Task] Sending image {image_id} to MakeIt3D")

        response = requests.post(
            "https://api.makeit3d.io/api/v1/dream/",
            json={"image_url": image_url},
            headers={
                "Authorization": f"Token {MAKEIT3D_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=30
        )

        if response.status_code >= 500:
            raise Exception("MakeIt3D API server error")

        if response.status_code >= 400:
            logger.warning(f"[Task] MakeIt3D error: {response.status_code} - {response.text}")
            supabase.table("images").update({
                "status": "error",
                "error_message": f"MakeIt3D API returned {response.status_code}"
            }).eq("id", image_id).execute()
            return

        result = response.json()
        output_url = result.get("output_url")

        if not output_url:
            raise Exception("MakeIt3D did not return output_url")

        supabase.table("images").update({
            "status": "processed",
            "processed_url": output_url
        }).eq("id", image_id).execute()

        logger.info(f"[Task] Image {image_id} processed by MakeIt3D")
        return {"status": "done", "image_id": image_id}

    except Exception as e:
        logger.error(f"[Task] Error processing image {image_id}: {e}")
        supabase.table("images").update({
            "status": "error",
            "error_message": str(e)
        }).eq("id", image_id).execute()
        raise self.retry(exc=e)