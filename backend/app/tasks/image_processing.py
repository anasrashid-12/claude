import io
import os
from PIL import Image as PILImage
from app.core.celery import celery_app
from app.services.image import image_service
from app.services.task import task_service, TaskService
from app.models.image import ProcessingStatus, ProcessingType
from app.models.task import TaskType, TaskStatus
from app.core.storage import storage_client
import requests
from typing import List, Dict, Any, Optional
import time
import httpx
from ..database import Database
from celery import Task
from rembg import remove
import cv2
import numpy as np
from app.core.celery_app import celery_app
from app.services.image_processor import ImageProcessor
import asyncio
from app.core.database import Database, SessionLocal
from app.core.config import settings
import logging
from typing import Optional, Tuple
import tempfile
from datetime import datetime
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

class ImageProcessingTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        try:
            db = SessionLocal()
            task_service = TaskService(db)
            task = task_service.get_task_by_celery_id(task_id)
            if task:
                task_service.update_task(
                    task_id=task.id,
                    status=TaskStatus.FAILED,
                    error=str(exc)
                )
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
        finally:
            db.close()

@celery_app.task(
    bind=True,
    base=ImageProcessingTask,
    name="process_image",
    max_retries=3,
    default_retry_delay=60
)
def process_image(self, image_url: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Process an image with the given options"""
    try:
        # Initialize database session and service
        db = SessionLocal()
        task_service = TaskService(db)
        
        # Create task record
        task = task_service.create_task(
            store_id=options.get("store_id"),
            task_type=TaskType.IMAGE_PROCESSING,
            celery_task_id=self.request.id,
            metadata={"image_url": image_url, "options": options}
        )
        
        try:
            # Update task status to processing
            task_service.update_task(
                task_id=task.id,
                status=TaskStatus.PROCESSING,
                progress=0
            )
            
            # Download image
            image_data = download_image(image_url)
            
            # Process image
            processed_data = apply_image_processing(image_data, options)
            
            # Upload processed image
            result_url = upload_processed_image(processed_data, task.id)
            
            # Update task with success
            task_service.update_task(
                task_id=task.id,
                status=TaskStatus.COMPLETED,
                progress=100,
                result={"processed_url": result_url}
            )
            
            return {
                "task_id": str(task.id),
                "status": "completed",
                "result_url": result_url
            }
            
        except Exception as e:
            # Update task with error
            task_service.update_task(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=str(e)
            )
            raise
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Image processing failed: {e}")
        raise

def download_image(url: str) -> bytes:
    """Download image from URL"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logger.error(f"Failed to download image: {e}")
        raise

def upload_processed_image(image_bytes: bytes, task_id: str) -> str:
    """Upload processed image to storage"""
    try:
        from app.core.storage import upload_file
        filename = f"processed_{task_id}.png"
        return upload_file(image_bytes, filename, "image/png")
    except Exception as e:
        logger.error(f"Failed to upload processed image: {e}")
        raise

def apply_image_processing(image_bytes: bytes, options: Dict[str, Any]) -> bytes:
    """Apply image processing operations"""
    try:
        # Load image
        img = PILImage.open(io.BytesIO(image_bytes))
        
        # Apply processing operations
        if options.get("remove_background"):
            img = remove_background(img, options.get("background_options"))
            
        if options.get("resize"):
            img = resize_image(img, options.get("resize_options"))
            
        if options.get("optimize", True):
            img = optimize_image(img, options.get("optimize_options"))
            
        # Convert back to bytes
        output = io.BytesIO()
        img.save(output, format="PNG", optimize=True)
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Failed to process image: {e}")
        raise

def remove_background(img: PILImage.Image, options: Dict = None) -> PILImage.Image:
    """Remove image background"""
    try:
        from rembg import remove
        return remove(img)
    except Exception as e:
        logger.error(f"Failed to remove background: {e}")
        raise

def resize_image(img: PILImage.Image, options: Dict = None) -> PILImage.Image:
    """Resize image"""
    try:
        if not options:
            return img
            
        width = options.get("width")
        height = options.get("height")
        maintain_aspect = options.get("maintain_aspect", True)
        
        if maintain_aspect:
            img.thumbnail((width, height))
            return img
        else:
            return img.resize((width, height))
            
    except Exception as e:
        logger.error(f"Failed to resize image: {e}")
        raise

def optimize_image(img: PILImage.Image, options: Dict = None) -> PILImage.Image:
    """Optimize image for web"""
    try:
        if not options:
            options = {}
            
        quality = options.get("quality", 85)
        format = options.get("format", "PNG")
        
        output = io.BytesIO()
        img.save(output, format=format, quality=quality, optimize=True)
        return PILImage.open(output)
        
    except Exception as e:
        logger.error(f"Failed to optimize image: {e}")
        raise

@celery_app.task
def cleanup_processed_images() -> None:
    """Periodic task to cleanup temporary processed images"""
    logger.info("Starting cleanup of processed images")
    # Implement cleanup logic here
    pass 