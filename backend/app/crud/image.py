from typing import Optional, List, Dict, Any
from app.crud.base_supabase import CRUDBase
from app.models.image import Image, ImageCreate, ImageUpdate
from app.core.supabase import supabase

class CRUDImage(CRUDBase[Image, ImageCreate, ImageUpdate]):
    async def get_by_product_id(self, product_id: str) -> List[Image]:
        """
        Get all images for a specific product.
        """
        response = (
            supabase.table(self.table_name)
            .select("*")
            .eq("product_id", product_id)
            .execute()
        )
        return [self.model(**item) for item in response.data]

    async def get_by_shopify_id(self, shopify_id: str) -> Optional[Image]:
        """
        Get image by Shopify ID.
        """
        response = (
            supabase.table(self.table_name)
            .select("*")
            .eq("shopify_id", shopify_id)
            .execute()
        )
        data = response.data
        if not data:
            return None
        return self.model(**data[0])

    async def get_processing_history(self, image_id: str) -> List[Dict[str, Any]]:
        """
        Get processing history for an image.
        """
        response = (
            supabase.table("image_processing_history")
            .select("*")
            .eq("image_id", image_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data

    async def add_processing_history(
        self,
        image_id: str,
        operation: str,
        status: str,
        processing_time: int,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a processing history entry for an image.
        """
        history_data = {
            "image_id": image_id,
            "operation": operation,
            "status": status,
            "processing_time": processing_time,
            "error_message": error_message
        }
        response = (
            supabase.table("image_processing_history")
            .insert(history_data)
            .execute()
        )
        return response.data[0]

image_crud = CRUDImage(model=Image, table_name="images") 