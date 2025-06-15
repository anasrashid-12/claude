from celery_app import celery
from supabase import create_client
import os
import requests
import logging

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase credentials not set in environment")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

logger = logging.getLogger(__name__)

@celery.task(name="process_image_task", bind=True, max_retries=3, default_retry_delay=10)
def process_image_task(self, image_id: str, image_url: str):
    try:
        logger.info(f"Processing image: {image_id}")

        # Send image to AI service
        response = requests.post("http://ai-api:8000/process", json={"image_url": image_url})

        if response.status_code >= 500:
            raise Exception("AI processing failed (server error)")

        if response.status_code >= 400:
            supabase.table("images").update({
                "status": "error",
                "error_message": f"AI API returned {response.status_code}"
            }).eq("id", image_id).execute()
            return

        result = response.json()
        output_url = result.get("output_url")

        supabase.table("images").update({
            "status": "processed",
            "processed_url": output_url
        }).eq("id", image_id).execute()

        logger.info(f"Image {image_id} processed.")

        return {"status": "done", "image_id": image_id}

    except Exception as e:
        logger.error(f"Error processing image {image_id}: {e}")

        supabase.table("images").update({
            "status": "error",
            "error_message": str(e)
        }).eq("id", image_id).execute()

        raise self.retry(exc=e)
