from typing import Optional, List
from app.models.image import Image, ImageCreate, ImageUpdate, ProcessingStatus
from app.repositories.base import BaseRepository
from datetime import datetime

class ImageRepository(BaseRepository[Image, ImageCreate, ImageUpdate]):
    def __init__(self):
        super().__init__(Image, "images")

    async def get_by_product(self, store_id: int, product_id: str) -> List[Image]:
        """Get all images for a product"""
        result = self.db.client.table(self.table_name)\
            .select("*")\
            .eq("store_id", store_id)\
            .eq("product_id", product_id)\
            .execute()
        return [Image(**item) for item in result.data]

    async def get_by_image_id(self, store_id: int, image_id: str) -> Optional[Image]:
        """Get image by Shopify image ID"""
        result = self.db.client.table(self.table_name)\
            .select("*")\
            .eq("store_id", store_id)\
            .eq("image_id", image_id)\
            .order("version", desc=True)\
            .limit(1)\
            .execute()
        return Image(**result.data[0]) if result.data else None

    async def update_status(
        self,
        id: int,
        status: ProcessingStatus,
        error_message: Optional[str] = None
    ) -> Optional[Image]:
        """Update image processing status"""
        data = {
            "status": status,
            "error_message": error_message,
        }
        
        if status == ProcessingStatus.PROCESSING:
            data["processing_started_at"] = datetime.utcnow()
        elif status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]:
            data["processing_completed_at"] = datetime.utcnow()
        
        result = self.db.client.table(self.table_name)\
            .update(data)\
            .eq("id", id)\
            .execute()
        return Image(**result.data[0]) if result.data else None

    async def get_pending_images(self, limit: int = 10) -> List[Image]:
        """Get pending images for processing"""
        result = self.db.client.table(self.table_name)\
            .select("*")\
            .eq("status", ProcessingStatus.PENDING)\
            .order("created_at")\
            .limit(limit)\
            .execute()
        return [Image(**item) for item in result.data]

    async def get_processing_stats(self, store_id: int) -> dict:
        """Get processing statistics for a store"""
        result = self.db.client.table(self.table_name)\
            .select("status", count="exact")\
            .eq("store_id", store_id)\
            .group_by("status")\
            .execute()
        
        stats = {
            "total": 0,
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0
        }
        
        for row in result.data:
            status = row["status"]
            count = row["count"]
            stats[status] = count
            stats["total"] += count
        
        return stats 