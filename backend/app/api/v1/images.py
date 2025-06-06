from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from typing import List, Optional
from ....models import Shop, ImageJob, ProcessingType
from ....services.image_service import ImageService
from ....core.auth import get_current_shop

router = APIRouter()

@router.post("/process", response_model=ImageJob)
async def create_processing_job(
    image_url: str,
    processing_types: List[ProcessingType],
    product_id: Optional[str] = None,
    shop: Shop = Depends(get_current_shop),
    image_service: ImageService = Depends()
):
    """Create a new image processing job"""
    try:
        return await image_service.create_job(
            shop_id=shop.id,
            image_url=image_url,
            processing_type=processing_types,
            product_id=product_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bulk-process", response_model=List[ImageJob])
async def create_bulk_processing_jobs(
    image_urls: List[str],
    processing_types: List[ProcessingType],
    product_ids: Optional[List[str]] = None,
    shop: Shop = Depends(get_current_shop),
    image_service: ImageService = Depends()
):
    """Create multiple image processing jobs"""
    try:
        jobs = []
        for i, url in enumerate(image_urls):
            product_id = product_ids[i] if product_ids and i < len(product_ids) else None
            job = await image_service.create_job(
                shop_id=shop.id,
                image_url=url,
                processing_type=processing_types,
                product_id=product_id
            )
            jobs.append(job)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/jobs", response_model=List[ImageJob])
async def list_jobs(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    shop: Shop = Depends(get_current_shop),
    image_service: ImageService = Depends()
):
    """List image processing jobs"""
    try:
        return await image_service.list_jobs(
            shop_id=shop.id,
            status=status,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/jobs/{job_id}", response_model=ImageJob)
async def get_job(
    job_id: str,
    shop: Shop = Depends(get_current_shop),
    image_service: ImageService = Depends()
):
    """Get specific job details"""
    try:
        job = await image_service.get_job(job_id)
        if job.shop_id != shop.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this job")
        return job
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/jobs/{job_id}")
async def cancel_job(
    job_id: str,
    shop: Shop = Depends(get_current_shop),
    image_service: ImageService = Depends()
):
    """Cancel a processing job"""
    try:
        await image_service.cancel_job(job_id, shop.id)
        return {"message": "Job cancelled successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 