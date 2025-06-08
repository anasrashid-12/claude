from typing import Optional, Dict, List
from PIL import Image as PILImage
import io
import uuid
from datetime import datetime
from app.core.supabase import SupabaseClient
from app.models.image import ProcessingType, ProcessingStatus, Image, ProcessingHistory
from app.core.config import settings
import httpx
import asyncio
from app.core.exceptions import ImageProcessingError
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.supabase = SupabaseClient.get_client()
        self.ai_enabled = bool(settings.AI_API_KEY and settings.AI_API_URL)
        if not self.ai_enabled:
            logger.warning("AI services not configured. Some image processing features will be limited.")

    async def process_image(
        self,
        image_id: str,
        processing_types: List[ProcessingType],
        settings: Optional[Dict] = None
    ) -> Image:
        """Process an image with specified operations"""
        try:
            # Get image from Supabase
            image_data = self.supabase.table('images').select('*').eq('id', image_id).single().execute()
            image = Image(**image_data.data)

            # Create processing history entry
            for proc_type in processing_types:
                history = ProcessingHistory(
                    image_id=image.id,
                    operation=proc_type,
                    status=ProcessingStatus.PROCESSING,
                    settings=settings
                )
                history_data = history.model_dump()
                self.supabase.table('processing_history').insert(history_data).execute()

            # Download image
            async with httpx.AsyncClient() as client:
                response = await client.get(image.original_url)
                img = PILImage.open(io.BytesIO(response.content))

            # Process image with each operation
            for proc_type in processing_types:
                if proc_type == ProcessingType.BACKGROUND_REMOVAL:
                    if not self.ai_enabled:
                        logger.warning("Background removal requested but AI services not configured. Skipping.")
                        continue
                    img = await self._remove_background(img)
                elif proc_type == ProcessingType.RESIZE:
                    img = await self._resize_image(img, settings)
                elif proc_type == ProcessingType.OPTIMIZE:
                    img = await self._optimize_image(img, settings)

            # Save processed image
            output = io.BytesIO()
            img.save(output, format='PNG')
            output.seek(0)

            # Upload to Supabase Storage
            file_path = f"processed/{image_id}/{uuid.uuid4()}.png"
            self.supabase.storage.from_(settings.STORAGE_BUCKET_NAME).upload(
                file_path,
                output.getvalue()
            )

            # Get public URL
            public_url = self.supabase.storage.from_(settings.STORAGE_BUCKET_NAME).get_public_url(file_path)

            # Update image record
            self.supabase.table('images').update({
                'current_url': public_url,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', image_id).execute()

            # Update processing history
            self.supabase.table('processing_history').update({
                'status': ProcessingStatus.COMPLETED,
                'completed_at': datetime.utcnow().isoformat()
            }).eq('image_id', image_id).execute()

            return image

        except Exception as e:
            # Update processing history with error
            self.supabase.table('processing_history').update({
                'status': ProcessingStatus.FAILED,
                'error_message': str(e),
                'completed_at': datetime.utcnow().isoformat()
            }).eq('image_id', image_id).execute()
            raise ImageProcessingError(f"Failed to process image: {str(e)}")

    async def _remove_background(self, img: PILImage.Image) -> PILImage.Image:
        """Remove background using AI API"""
        if not self.ai_enabled:
            raise ImageProcessingError("Background removal not available - AI services not configured")
        
        try:
            # Convert image to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            # Call AI API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.AI_API_URL}/remove-background",
                    headers={"Authorization": f"Bearer {settings.AI_API_KEY}"},
                    files={"image": ("image.png", img_byte_arr, "image/png")}
                )
                response.raise_for_status()

            # Convert response to PIL Image
            return PILImage.open(io.BytesIO(response.content))
        except Exception as e:
            raise ImageProcessingError(f"Background removal failed: {str(e)}")

    async def _resize_image(
        self,
        img: PILImage.Image,
        settings: Optional[Dict] = None
    ) -> PILImage.Image:
        """Resize image according to settings"""
        if not settings or 'width' not in settings or 'height' not in settings:
            return img
        
        width = settings['width']
        height = settings['height']
        
        if width and height:
            return img.resize((width, height), PILImage.LANCZOS)
        elif width:
            ratio = width / img.width
            height = int(img.height * ratio)
            return img.resize((width, height), PILImage.LANCZOS)
        elif height:
            ratio = height / img.height
            width = int(img.width * ratio)
            return img.resize((width, height), PILImage.LANCZOS)
        
        return img

    async def _optimize_image(
        self,
        img: PILImage.Image,
        settings: Optional[Dict] = None
    ) -> PILImage.Image:
        """Optimize image for web"""
        if not settings:
            settings = {}

        quality = settings.get('quality', 85)
        format = settings.get('format', 'WEBP')

        output = io.BytesIO()
        img.save(output, format=format, quality=quality, optimize=True)
        output.seek(0)
        return PILImage.open(output)

    async def bulk_process(
        self,
        image_ids: List[str],
        processing_types: List[ProcessingType],
        settings: Optional[Dict] = None
    ) -> List[Image]:
        """Process multiple images concurrently"""
        results = []
        for image_id in image_ids:
            try:
                processed = await self.process_image(image_id, processing_types, settings)
                results.append(processed)
            except Exception as e:
                logger.error(f"Failed to process image {image_id}: {str(e)}")
                continue
        return results 