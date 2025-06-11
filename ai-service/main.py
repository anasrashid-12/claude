import os
from celery import Celery
from dotenv import load_dotenv
import logging
from typing import List, Dict, Any, Optional
import requests
import httpx
from image_processor import ImageProcessor
import io

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    'image_processing',
    broker=os.getenv('REDIS_URL', 'redis://redis:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://redis:6379/0')
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    worker_prefetch_multiplier=1,  # Process one task at a time
)

# Initialize image processor
processor = ImageProcessor()

class ImageProcessingError(Exception):
    """Custom exception for image processing errors"""
    pass

def download_image(url: str) -> bytes:
    """Download image from URL"""
    try:
        response = httpx.get(url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logger.error(f"Failed to download image from {url}: {str(e)}")
        raise ImageProcessingError(f"Failed to download image: {str(e)}")

@celery_app.task(bind=True, name="process_image")
def process_image(self, image_url: str, process_type: str, 
                 params: Dict[str, Any] = None, task_id: str = None):
    """
    Process a single image asynchronously.
    
    Args:
        image_url: URL of the image to process
        process_type: Type of processing to apply
        params: Processing parameters
        task_id: Optional task ID for tracking
    """
    logger.info(f"Starting image processing task: {task_id or self.request.id}")
    
    try:
        # Update task status
        self.update_state(state="DOWNLOADING")
        
        # Download image
        image_data = download_image(image_url)
        
        # Update task status
        self.update_state(state="PROCESSING")
        
        # Process image based on type
        if process_type == "background_removal":
            result = processor.remove_background(image_data)
        elif process_type == "enhance":
            result = processor.enhance_image(image_data, params)
        elif process_type == "resize":
            if not params or "target_size" not in params:
                raise ImageProcessingError("Target size required for resize")
            result = processor.resize_image(image_data, params["target_size"])
        elif process_type == "optimize":
            result = processor.optimize_image(image_data, params.get("quality", 85) if params else 85)
        elif process_type == "auto_crop":
            result = processor.auto_crop(image_data)
        else:
            raise ImageProcessingError(f"Invalid process type: {process_type}")
        
        # Return result
        return {
            "status": "success",
            "task_id": task_id,
            "process_type": process_type,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Image processing failed: {str(e)}")
        # Update task status to failed
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
                       params: Dict[str, Any] = None):
    """
    Process multiple images in bulk.
    
    Args:
        image_urls: List of image URLs to process
        process_type: Type of processing to apply
        params: Processing parameters
    """
    logger.info(f"Starting bulk processing task for {len(image_urls)} images")
    
    results = []
    errors = []
    total_images = len(image_urls)
    
    for i, url in enumerate(image_urls, 1):
        try:
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'current': i, 'total': total_images}
            )
            
            # Process image
            result = process_image.delay(
                image_url=url,
                process_type=process_type,
                params=params,
                task_id=f"{self.request.id}_{i}"
            )
            
            results.append({
                "url": url,
                "task_id": result.id,
                "status": "submitted"
            })
            
        except Exception as e:
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