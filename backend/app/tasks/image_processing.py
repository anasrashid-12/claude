import io
import os
from PIL import Image as PILImage
from app.core.celery import celery_app
from app.services.image import image_service
from app.services.task import task_service
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

class ImageProcessingTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        image_id = args[0] if args else None
        if image_id:
            processor = ImageProcessor()
            asyncio.run(processor.update_status(
                image_id=image_id,
                status=ProcessingStatus.FAILED,
                error_message=str(exc)
            ))
        super().on_failure(exc, task_id, args, kwargs, einfo)

@celery_app.task(base=ImageProcessingTask, bind=True)
def process_image(
    self,
    image_id: str,
    processing_types: List[ProcessingType],
    settings: Optional[Dict] = None
) -> Dict[str, Any]:
    """Process a single image"""
    try:
        processor = ImageProcessor()
        result = asyncio.run(processor.process_image(
            image_id=image_id,
            processing_types=processing_types,
            settings=settings
        ))
        return {
            "status": "success",
            "image_id": image_id,
            "processed_url": result.current_url
        }
    except Exception as e:
        return {
            "status": "error",
            "image_id": image_id,
            "error": str(e)
        }

@celery_app.task(
    name="app.tasks.image_processing.bulk_process",
    bind=True
)
def bulk_process(
    self,
    image_ids: List[str],
    processing_types: List[ProcessingType],
    settings: Optional[Dict] = None
) -> Dict[str, Any]:
    """Process multiple images"""
    try:
        processor = ImageProcessor()
        results = asyncio.run(processor.bulk_process(
            image_ids=image_ids,
            processing_types=processing_types,
            settings=settings
        ))

        successful = []
        failed = []

        for result in results:
            if isinstance(result, Exception):
                failed.append({
                    "image_id": image_ids[results.index(result)],
                    "error": str(result)
                })
            else:
                successful.append({
                    "image_id": result.id,
                    "processed_url": result.current_url
                })

        return {
            "status": "completed",
            "successful": successful,
            "failed": failed,
            "total_processed": len(successful),
            "total_failed": len(failed)
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "successful": [],
            "failed": image_ids
        }

def remove_background(img: PILImage.Image, options: Dict = None) -> PILImage.Image:
    """
    Remove image background using AI
    TODO: Implement actual background removal using AI service
    """
    # Placeholder implementation
    time.sleep(2)  # Simulate processing time
    return img

def resize_image(img: PILImage.Image, options: Dict = None) -> PILImage.Image:
    """Resize image while maintaining aspect ratio"""
    if not options:
        return img

    max_width = options.get('max_width', 1024)
    max_height = options.get('max_height', 1024)
    
    if img.width > max_width or img.height > max_height:
        ratio = min(max_width/img.width, max_height/img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, PILImage.LANCZOS)
    
    return img

def optimize_image(img: PILImage.Image, options: Dict = None) -> PILImage.Image:
    """Optimize image for web delivery"""
    if not options:
        return img

    quality = options.get('quality', 85)
    format_type = options.get('format', 'PNG')
    
    output = io.BytesIO()
    img.save(output, format=format_type, quality=quality, optimize=True)
    output.seek(0)
    return PILImage.open(output) 