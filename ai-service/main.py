import os
import logging
import httpx
import io
from dotenv import load_dotenv
from celery import Celery
from typing import List, Dict, Any, Optional
from image_processor import ImageProcessor

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    'image_processing',
    broker=os.getenv('REDIS_URL', 'redis://redis:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://redis:6379/0')
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_prefetch_multiplier=1,
)

processor = ImageProcessor()


class ImageProcessingError(Exception):
    pass


def download_image(url: str, timeout: int = 15) -> bytes:
    try:
        response = httpx.get(url, timeout=timeout)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logger.error(f"Download failed for {url}: {str(e)}")
        raise ImageProcessingError(f"Failed to download image: {str(e)}")


@celery_app.task(bind=True, name="process_image")
def process_image(self, image_url: str, process_type: str,
                  params: Optional[Dict[str, Any]] = None,
                  task_id: Optional[str] = None):
    logger.info(f"Processing task started: {task_id or self.request.id}")

    try:
        self.update_state(state="DOWNLOADING")
        image_data = download_image(image_url)

        self.update_state(state="PROCESSING")
        params = params or {}

        if process_type == "background_removal":
            result = processor.remove_background(image_data)
        elif process_type == "enhance":
            result = processor.enhance_image(image_data, params)
        elif process_type == "resize":
            if "target_size" not in params:
                raise ImageProcessingError("Missing 'target_size' for resize")
            result = processor.resize_image(image_data, params["target_size"])
        elif process_type == "optimize":
            quality = params.get("quality", 85)
            result = processor.optimize_image(image_data, quality)
        elif process_type == "auto_crop":
            result = processor.auto_crop(image_data)
        else:
            raise ImageProcessingError(f"Unknown process_type: {process_type}")

        return {
            "status": "success",
            "task_id": task_id or self.request.id,
            "process_type": process_type,
            "result": result
        }

    except Exception as e:
        logger.error(f"Error during image processing: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={
                "exc_type": type(e).__name__,
                "exc_message": str(e),
                "task_id": task_id or self.request.id
            }
        )
        raise


@celery_app.task(bind=True, name="bulk_process_images")
def bulk_process_images(self, image_urls: List[str],
                        process_type: str,
                        params: Optional[Dict[str, Any]] = None):
    logger.info(f"Bulk processing {len(image_urls)} images")

    results = []
    errors = []

    for i, url in enumerate(image_urls, start=1):
        try:
            self.update_state(
                state='PROGRESS',
                meta={'current': i, 'total': len(image_urls)}
            )

            task = process_image.apply_async(
                kwargs={
                    'image_url': url,
                    'process_type': process_type,
                    'params': params or {},
                    'task_id': f"{self.request.id}_{i}"
                }
            )

            results.append({
                "url": url,
                "task_id": task.id,
                "status": "submitted"
            })

        except Exception as e:
            logger.error(f"Error submitting image {url}: {str(e)}")
            errors.append({
                "url": url,
                "error": str(e)
            })

    return {
        "status": "completed",
        "total_processed": len(results),
        "total_errors": len(errors),
        "results": results,
        "errors": errors
    }
