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
from typing import List, Dict, Any
import time

@celery_app.task(
    name="app.tasks.image_processing.process_image",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def process_image(self, image_id: int) -> Dict[str, Any]:
    """
    Process a single image with specified processing types
    """
    try:
        # Update task status
        task = task_service.update_status(
            self.request.id,
            TaskStatus.STARTED
        )

        # Get image record
        image = image_service.get(image_id)
        if not image:
            raise ValueError(f"Image {image_id} not found")

        # Update image status
        image = image_service.update_status(
            image_id,
            ProcessingStatus.PROCESSING
        )

        # Download original image
        response = requests.get(image.original_url)
        response.raise_for_status()
        img = PILImage.open(io.BytesIO(response.content))

        # Process image based on processing types
        for proc_type in image.processing_types:
            if proc_type == ProcessingType.BACKGROUND_REMOVAL:
                img = remove_background(img, image.processing_options)
            elif proc_type == ProcessingType.RESIZE:
                img = resize_image(img, image.processing_options)
            elif proc_type == ProcessingType.OPTIMIZE:
                img = optimize_image(img, image.processing_options)

        # Save processed image
        output = io.BytesIO()
        img.save(output, format=img.format or 'PNG')
        output.seek(0)

        # Upload to storage
        filename = f"{image.store_id}/{image.product_id}/{image.image_id}_{image.version}.png"
        processed_url = storage_client.upload_file(
            filename,
            output,
            content_type="image/png"
        )

        # Update image record
        image = image_service.update_status(
            image_id,
            ProcessingStatus.COMPLETED,
            processed_url=processed_url
        )

        # Update task status
        task = task_service.update_status(
            self.request.id,
            TaskStatus.SUCCESS,
            result={
                "processed_url": processed_url,
                "processing_types": [pt.value for pt in image.processing_types]
            }
        )

        return {
            "status": "success",
            "image_id": image_id,
            "processed_url": processed_url
        }

    except Exception as e:
        # Update image status
        image_service.update_status(
            image_id,
            ProcessingStatus.FAILED,
            error_message=str(e)
        )

        # Update task status
        task_service.update_status(
            self.request.id,
            TaskStatus.FAILURE,
            error_message=str(e)
        )

        # Retry if possible
        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            return {
                "status": "error",
                "image_id": image_id,
                "error": str(e)
            }

@celery_app.task(
    name="app.tasks.image_processing.bulk_process",
    bind=True
)
def bulk_process(self, image_ids: List[int]) -> Dict[str, Any]:
    """
    Process multiple images in bulk
    """
    results = []
    for image_id in image_ids:
        try:
            result = process_image.delay(image_id)
            results.append({
                "image_id": image_id,
                "task_id": result.id,
                "status": "queued"
            })
        except Exception as e:
            results.append({
                "image_id": image_id,
                "error": str(e),
                "status": "failed"
            })

    return {
        "status": "success",
        "total": len(image_ids),
        "results": results
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