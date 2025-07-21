from app.celery_app import celery_app
from supabase import create_client
import os, requests, logging, time, uuid

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
MAKEIT3D_API_KEY = os.getenv("MAKEIT3D_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
logger = logging.getLogger("image_tasks")


@celery_app.task(bind=True, max_retries=3)
def process_image_task(self, image_id: str, image_url: str, operation: str):
    try:
        client_task_id = f"{image_id}-{operation}-{uuid.uuid4().hex}"
        logger.info(f"[Task] 🚀 Starting task {client_task_id} for operation '{operation}'")

        endpoint_map = {
            "remove-background": {
                "url": "https://api.makeit3d.io/generate/remove-background",
                "payload": {
                    "task_id": client_task_id,
                    "provider": "stability",
                    "input_image_asset_url": image_url,
                    "output_format": "png"
                }
            },
            "upscale": {
                "url": "https://api.makeit3d.io/generate/upscale",
                "payload": {
                    "task_id": client_task_id,
                    "provider": "stability",
                    "input_image_asset_url": image_url,
                    "model": "fast",
                    "prompt": "high quality detailed image"
                }
            },
            "downscale": {
                "url": "https://api.makeit3d.io/generate/downscale",
                "payload": {
                    "task_id": client_task_id,
                    "input_image_asset_url": image_url,
                    "max_size_mb": 2.0,
                    "aspect_ratio_mode": "original",
                    "output_format": "jpeg"
                }
            }
        }

        if operation not in endpoint_map:
            logger.error(f"[Task] ❌ Unsupported operation: {operation}")
            raise ValueError(f"Unsupported operation: {operation}")

        api = endpoint_map[operation]
        response = requests.post(api["url"], headers={
            "X-API-Key": MAKEIT3D_API_KEY,
            "Content-Type": "application/json"
        }, json=api["payload"], timeout=30)
        response.raise_for_status()

        submit_data = response.json()
        real_task_id = submit_data.get("task_id") or client_task_id

        for attempt in range(60):
            time.sleep(5)
            poll_res = requests.get(f"https://api.makeit3d.io/tasks/{real_task_id}/status",
                                    headers={"X-API-Key": MAKEIT3D_API_KEY}, timeout=15)
            poll_res.raise_for_status()
            data = poll_res.json()

            if data.get("status") == "complete":
                processed_url = data.get("asset_url")
                logger.info(f"[Task] ✅ Processing complete | URL: {processed_url}")

                download_res = requests.get(processed_url, timeout=60)
                download_res.raise_for_status()
                image_bytes = download_res.content

                ext = ".png" if operation == "remove-background" else ".jpg"
                content_type = "image/png" if operation == "remove-background" else "image/jpeg"

                processed_filename = f"processed/{uuid.uuid4().hex}{ext}"
                upload_res = supabase.storage.from_("makeit3d-public").upload(
                    processed_filename,
                    image_bytes,
                    {"content-type": content_type}
                )

                if hasattr(upload_res, "error") and upload_res.error:
                    raise Exception(f"Failed to upload to Supabase: {upload_res.error}")

                permanent_url = f"{SUPABASE_URL}/storage/v1/object/public/makeit3d-public/{processed_filename}"

                # ✅ Update both processed_url & filename
                supabase.table("images").update({
                    "status": "processed",
                    "processed_url": permanent_url,
                    "filename": processed_filename   # Save for signed-url download
                }).eq("id", image_id).execute()

                logger.info(f"[Task] ✅ Saved in makeit3d-public/processed/ ✅ Permanent URL & filename saved ✅")
                return

            elif data.get("status") == "failed":
                raise Exception(f"Processing failed: {data.get('error', 'Unknown Error')}")

        raise TimeoutError("Timeout waiting for processing result")

    except Exception as e:
        logger.error(f"[Task] ❌ Exception on {image_id} | Error: {str(e)}")
        supabase.table("images").update({
            "status": "error",
            "error_message": str(e)
        }).eq("id", image_id).execute()
        raise self.retry(exc=e, countdown=300)
