import os
import requests
import time
from app.services.supabase_service import supabase
from app.logging_config import logger
from celery import shared_task

MAKEIT3D_API_KEY = os.getenv("MAKEIT3D_API_KEY")
MAKEIT3D_BASE_URL = "https://api.makeit3d.io"

headers = {
    "X-API-Key": MAKEIT3D_API_KEY,
    "Content-Type": "application/json",
}


@shared_task
def submit_job_task(image_id: str, operation: str, image_url: str):
    logger.info(f"Submitting job for image_id: {image_id}, operation: {operation}")

    payload = {"image_url": image_url}
    endpoint = ""

    if operation == "remove-background":
        endpoint = "/generate/remove-background"
    elif operation == "upscale":
        endpoint = "/generate/upscale"
    elif operation == "downscale":
        endpoint = "/generate/downscale"
    else:
        logger.error(f"Invalid operation: {operation}")
        supabase.table("images").update({"status": "failed"}).eq("id", image_id).execute()
        return

    try:
        res = requests.post(f"{MAKEIT3D_BASE_URL}{endpoint}", json=payload, headers=headers)
        res.raise_for_status()
        data = res.json()
        task_id = data.get("task_id")

        if not task_id:
            raise ValueError("task_id not found in response")

        supabase.table("images").update({
            "status": "processing",
            "external_task_id": task_id
        }).eq("id", image_id).execute()

        logger.info(f"Submitted job successfully for image {image_id} with task_id {task_id}")

    except Exception as e:
        logger.error(f"Failed to submit job: {e}")
        supabase.table("images").update({"status": "failed"}).eq("id", image_id).execute()


@shared_task
def poll_all_processing_images():
    logger.info("Polling all processing images...")

    try:
        response = supabase.table("images").select("*").eq("status", "processing").execute()
        images = response.data or []

        for img in images:
            task_id = img.get("external_task_id")
            image_id = img.get("id")

            try:
                res = requests.get(f"{MAKEIT3D_BASE_URL}/tasks/{task_id}/status", headers=headers)
                res.raise_for_status()
                status_data = res.json()

                if status_data["status"] == "complete":
                    output_url = status_data.get("output_url")

                    if output_url:
                        supabase.table("images").update({
                            "status": "completed",
                            "processed_url": output_url
                        }).eq("id", image_id).execute()

                        logger.info(f"Image {image_id} completed and updated.")
                    else:
                        logger.warning(f"No output_url found for image {image_id}")

                elif status_data["status"] == "failed":
                    supabase.table("images").update({"status": "failed"}).eq("id", image_id).execute()
                    logger.warning(f"Image {image_id} failed processing.")

            except Exception as poll_error:
                logger.error(f"Polling failed for image {image_id}: {poll_error}")

    except Exception as fetch_error:
        logger.error(f"Failed to fetch processing images: {fetch_error}")
