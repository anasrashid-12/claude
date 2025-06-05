from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from pydantic import BaseModel

from app.services.image_processor import ImageProcessor
from app.core.config import settings

router = APIRouter()

class ImageProcessingSettings(BaseModel):
    quality: Optional[int] = 80
    format: Optional[str] = "webp"
    background_removal: Optional[bool] = False

class ImageResponse(BaseModel):
    id: str
    original_url: str
    processed_url: Optional[str]
    status: str
    created_at: str

@router.post("/process", response_model=ImageResponse)
async def process_image(
    file: UploadFile = File(...),
    settings: ImageProcessingSettings = ImageProcessingSettings()
):
    """
    Process an uploaded image with specified settings.
    """
    # Validate file size
    if file.size > settings.MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum limit of {settings.MAX_IMAGE_SIZE} bytes"
        )
    
    # Validate file format
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in settings.SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: {settings.SUPPORTED_FORMATS}"
        )
    
    # Process image
    try:
        processor = ImageProcessor()
        result = await processor.process(file, settings)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ImageResponse])
async def list_images(
    page: int = Query(1, gt=0),
    limit: int = Query(20, gt=0, le=100)
):
    """
    List processed images with pagination.
    """
    try:
        processor = ImageProcessor()
        images = await processor.list_images(page, limit)
        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(image_id: str):
    """
    Get details of a specific processed image.
    """
    try:
        processor = ImageProcessor()
        image = await processor.get_image(image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        return image
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 