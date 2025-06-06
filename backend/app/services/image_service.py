from typing import List, Optional
from ..models import ImageJob, ProcessingType, ProcessingStatus
from ..core.database import get_supabase
from ..core.celery import process_image_task
from datetime import datetime

class ImageService:
    def __init__(self):
        self.supabase = get_supabase()

    async def create_job(
        self,
        shop_id: str,
        image_url: str,
        processing_type: List[ProcessingType],
        product_id: Optional[str] = None
    ) -> ImageJob:
        """Create a new image processing job"""
        # Create job record
        job_data = {
            "shop_id": shop_id,
            "image_url": image_url,
            "processing_type": [pt.value for pt in processing_type],
            "status": ProcessingStatus.PENDING.value,
            "product_id": product_id,
            "metadata": {}
        }
        
        response = self.supabase.table("image_jobs").insert(job_data).execute()
        job = ImageJob(**response.data[0])
        
        # Queue processing task
        process_image_task.delay(
            job_id=job.id,
            image_url=image_url,
            processing_type=[pt.value for pt in processing_type]
        )
        
        return job

    async def get_job(self, job_id: str) -> Optional[ImageJob]:
        """Get job by ID"""
        response = self.supabase.table("image_jobs").select("*").eq("id", job_id).execute()
        
        if not response.data:
            return None
            
        return ImageJob(**response.data[0])

    async def list_jobs(
        self,
        shop_id: str,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ImageJob]:
        """List jobs for a shop"""
        query = self.supabase.table("image_jobs").select("*").eq("shop_id", shop_id)
        
        if status:
            query = query.eq("status", status)
            
        response = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        
        return [ImageJob(**job_data) for job_data in response.data]

    async def update_job_status(
        self,
        job_id: str,
        status: ProcessingStatus,
        result_url: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> ImageJob:
        """Update job status"""
        update_data = {
            "status": status.value,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if result_url:
            update_data["result_url"] = result_url
            
        if error_message:
            update_data["error_message"] = error_message
            
        if metadata:
            update_data["metadata"] = metadata
            
        response = self.supabase.table("image_jobs").update(update_data).eq("id", job_id).execute()
        
        return ImageJob(**response.data[0])

    async def cancel_job(self, job_id: str, shop_id: str):
        """Cancel a processing job"""
        # Verify job belongs to shop
        job = await self.get_job(job_id)
        if not job or job.shop_id != shop_id:
            raise ValueError("Job not found or not authorized")
            
        if job.status not in [ProcessingStatus.PENDING.value, ProcessingStatus.PROCESSING.value]:
            raise ValueError("Cannot cancel completed or failed jobs")
            
        # Update job status
        await self.update_job_status(
            job_id=job_id,
            status=ProcessingStatus.FAILED,
            error_message="Job cancelled by user"
        ) 