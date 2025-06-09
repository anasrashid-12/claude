import os
from celery import Celery
from dotenv import load_dotenv
import logging
from typing import List, Dict, Any
import requests
from image_processor import ImageProcessor
import io

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "ai_service",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
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
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download image from {url}: {str(e)}")
        raise ImageProcessingError(f"Failed to download image: {str(e)}")

@celery_app.task(bind=True, name="process_image")
def process_image(self, image_url: str, process_type: str, 
                 params: Dict[str, Any] = None, task_id: str = None):
    """
    Process an image using our custom image processor
    
    Args:
        image_url (str): URL of the image to process
        process_type (str): Type of processing to perform
        params (dict): Additional parameters for processing
        task_id (str, optional): Custom task ID for tracking
    
    Returns:
        dict: Processing results including processed image data
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
            processed_data = processor.remove_background(image_data)
        elif process_type == "enhance":
            processed_data = processor.enhance_image(image_data, params)
        elif process_type == "resize":
            if not params or 'size' not in params:
                raise ImageProcessingError("Size parameter required for resize")
            processed_data = processor.resize_image(
                image_data, 
                params['size'],
                params.get('maintain_aspect', True)
            )
        elif process_type == "optimize":
            processed_data = processor.optimize_image(
                image_data,
                quality=params.get('quality', 85) if params else 85
            )
        elif process_type == "auto_crop":
            processed_data = processor.auto_crop(image_data)
        else:
            raise ImageProcessingError(f"Unknown process type: {process_type}")
        
        # For demo purposes, we'll return the processed image data directly
        # In production, you should save this to a storage service
        return {
            "status": "success",
            "task_id": task_id or self.request.id,
            "process_type": process_type,
            "processed_image_data": processed_data,
            "metadata": {
                "process_type": process_type,
                "parameters": params
            }
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
    Process multiple images in bulk
    
    Args:
        image_urls (list): List of image URLs to process
        process_type (str): Type of processing to perform
        params (dict): Additional parameters for processing
    
    Returns:
        list: List of processing results
    """
    logger.info(f"Starting bulk processing task for {len(image_urls)} images")
    
    results = []
    total_images = len(image_urls)
    
    for index, image_url in enumerate(image_urls, 1):
        try:
            # Create subtask for each image
            task_id = f"{self.request.id}_{index}"
            result = process_image.delay(
                image_url, 
                process_type, 
                params,
                task_id
            )
            results.append({
                "image_url": image_url,
                "task_id": task_id,
                "status": "submitted"
            })
            
            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": index,
                    "total": total_images,
                    "results": results
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to process image {image_url}: {str(e)}")
            results.append({
                "image_url": image_url,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "status": "completed",
        "total_processed": total_images,
        "results": results
    } 