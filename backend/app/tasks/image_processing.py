from ..core.celery_app import celery_app
from ..database import Database
from PIL import Image
import requests
from io import BytesIO
import os
from typing import Optional, Dict, Any
import time

db = Database()

@celery_app.task(name="process_image")
async def process_image(
    image_id: str,
    operation: str,
    settings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process an image with the specified operation."""
    try:
        # Get image from database
        image = await db.get_image(image_id)
        if not image:
            raise ValueError(f"Image {image_id} not found")

        # Create processing history entry
        history = await db.create_processing_history(
            image_id=image_id,
            operation=operation,
            settings=settings
        )

        # Download the image
        response = requests.get(image['original_url'])
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))

        # Process the image based on operation
        if operation == 'background_removal':
            # TODO: Implement background removal using AI API
            processed_img = await remove_background(img, settings)
        elif operation == 'resize':
            processed_img = await resize_image(img, settings)
        elif operation == 'optimize':
            processed_img = await optimize_image(img, settings)
        else:
            raise ValueError(f"Unknown operation: {operation}")

        # Save the processed image
        output = BytesIO()
        processed_img.save(output, format=img.format or 'PNG')
        output.seek(0)

        # Upload to storage
        storage_path = f"processed/{image_id}/{int(time.time())}.{img.format.lower()}"
        storage_url = await upload_to_storage(output, storage_path)

        # Create image version
        version = await db.create_image_version(
            image_id=image_id,
            storage_url=storage_url,
            processing_history_id=history['id']
        )

        # Update image current URL
        await db.update_image(image_id, {'current_url': storage_url})

        # Update processing history
        await db.update_processing_status(
            history['id'],
            status='completed',
            backup_url=storage_url
        )

        return {
            "status": "success",
            "image_id": image_id,
            "storage_url": storage_url,
            "version_id": version['id']
        }

    except Exception as e:
        # Update processing history with error
        if 'history' in locals():
            await db.update_processing_status(
                history['id'],
                status='failed',
                error_message=str(e)
            )
        raise

async def remove_background(img: Image.Image, settings: Optional[Dict[str, Any]] = None) -> Image.Image:
    """Remove background from image using AI API."""
    # TODO: Implement background removal using AI API
    return img

async def resize_image(img: Image.Image, settings: Optional[Dict[str, Any]] = None) -> Image.Image:
    """Resize image while maintaining aspect ratio."""
    if not settings or 'width' not in settings:
        return img

    target_width = settings['width']
    ratio = target_width / img.width
    target_height = int(img.height * ratio)

    return img.resize((target_width, target_height), Image.Resampling.LANCZOS)

async def optimize_image(img: Image.Image, settings: Optional[Dict[str, Any]] = None) -> Image.Image:
    """Optimize image for web delivery."""
    # Convert to RGB if necessary
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    # Apply quality reduction if specified
    quality = settings.get('quality', 85) if settings else 85
    
    output = BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    
    return Image.open(output)

async def upload_to_storage(file: BytesIO, path: str) -> str:
    """Upload file to storage and return public URL."""
    # TODO: Implement storage upload using Supabase storage
    return f"https://storage.example.com/{path}" 