from typing import List, Optional, Dict
from app.models.image import Image, ImageCreate, ImageUpdate, ProcessingStatus, ProcessingType
from app.repositories.image import ImageRepository
from app.services.base import BaseService
from app.core.celery import celery_app
from app.core.exceptions import ValidationError, NotFoundError
from app.services.store import store_service

class ImageService(BaseService[Image, ImageCreate, ImageUpdate, ImageRepository]):
    def __init__(self):
        super().__init__(ImageRepository)

    async def get_by_product(self, store_id: int, product_id: str) -> List[Image]:
        """Get all images for a product"""
        return await self.repository.get_by_product(store_id, product_id)

    async def get_by_image_id(self, store_id: int, image_id: str) -> Optional[Image]:
        """Get image by Shopify image ID"""
        return await self.repository.get_by_image_id(store_id, image_id)

    async def process_image(
        self,
        store_id: int,
        product_id: str,
        image_id: str,
        original_url: str,
        processing_types: List[ProcessingType],
        processing_options: Optional[Dict] = None,
        position: Optional[int] = None,
        alt_text: Optional[str] = None
    ) -> Image:
        """Create and process a new image"""
        # Validate store
        store = await store_service.get(store_id)
        if not store.is_active:
            raise ValidationError("Store is not active")

        # Create image record
        image_data = ImageCreate(
            store_id=store_id,
            product_id=product_id,
            image_id=image_id,
            original_url=original_url,
            processing_types=processing_types,
            processing_options=processing_options,
            position=position,
            alt_text=alt_text
        )
        
        image = await self.create(image_data)

        # Start processing task
        task = celery_app.send_task(
            "app.tasks.image_processing.process_image",
            args=[image.id],
            queue="image_processing"
        )

        # Update image with task ID
        await self.repository.update(
            image.id,
            ImageUpdate(task_id=task.id)
        )

        return image

    async def bulk_process_images(
        self,
        store_id: int,
        images: List[Dict]
    ) -> List[Image]:
        """Process multiple images"""
        # Validate store
        store = await store_service.get(store_id)
        if not store.is_active:
            raise ValidationError("Store is not active")

        processed_images = []
        for image_data in images:
            try:
                image = await self.process_image(
                    store_id=store_id,
                    product_id=image_data["product_id"],
                    image_id=image_data["image_id"],
                    original_url=image_data["original_url"],
                    processing_types=image_data["processing_types"],
                    processing_options=image_data.get("processing_options"),
                    position=image_data.get("position"),
                    alt_text=image_data.get("alt_text")
                )
                processed_images.append(image)
            except Exception as e:
                # Log error but continue processing other images
                print(f"Error processing image {image_data['image_id']}: {str(e)}")

        return processed_images

    async def update_status(
        self,
        image_id: int,
        status: ProcessingStatus,
        processed_url: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Image:
        """Update image processing status"""
        update_data = {
            "status": status,
            "error_message": error_message
        }
        
        if processed_url:
            update_data["processed_url"] = processed_url

        image = await self.repository.update_status(
            image_id,
            status,
            error_message
        )
        
        if not image:
            raise NotFoundError(f"Image with id {image_id} not found")
        
        return image

    async def get_processing_stats(self, store_id: int) -> dict:
        """Get processing statistics for a store"""
        return await self.repository.get_processing_stats(store_id)

    async def get_pending_images(self, limit: int = 10) -> List[Image]:
        """Get pending images for processing"""
        return await self.repository.get_pending_images(limit)

image_service = ImageService() 