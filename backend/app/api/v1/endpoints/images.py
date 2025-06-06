from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends
from pydantic import BaseModel

from app.services.image_processor import ImageProcessor
from app.core.config import settings
from app.services.image import image_service
from app.models.image import Image, ProcessingType
from app.models.store import Store
from app.core.exceptions import NotFoundError, ValidationError
from app.api.deps import get_current_store

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

class ProcessImageRequest(BaseModel):
    product_id: str
    image_id: str
    original_url: str
    processing_types: List[ProcessingType]
    processing_options: Optional[Dict] = None
    position: Optional[int] = None
    alt_text: Optional[str] = None

class BulkProcessRequest(BaseModel):
    images: List[ProcessImageRequest]

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

@router.post("", response_model=Image)
async def process_image_new(
    data: ProcessImageRequest,
    store: Store = Depends(get_current_store)
):
    """
    Process a single image
    """
    try:
        return await image_service.process_image(
            store_id=store.id,
            product_id=data.product_id,
            image_id=data.image_id,
            original_url=data.original_url,
            processing_types=data.processing_types,
            processing_options=data.processing_options,
            position=data.position,
            alt_text=data.alt_text
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bulk", response_model=List[Image])
async def bulk_process_images(
    data: BulkProcessRequest,
    store: Store = Depends(get_current_store)
):
    """
    Process multiple images
    """
    try:
        return await image_service.bulk_process_images(
            store_id=store.id,
            images=[img.dict() for img in data.images]
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/product/{product_id}", response_model=List[Image])
async def get_product_images(
    product_id: str,
    store: Store = Depends(get_current_store)
):
    """
    Get all images for a product
    """
    return await image_service.get_by_product(store.id, product_id)

@router.get("/{image_id}", response_model=Image)
async def get_image_new(
    image_id: str,
    store: Store = Depends(get_current_store)
):
    """
    Get image by ID
    """
    try:
        image = await image_service.get_by_image_id(store.id, image_id)
        if not image:
            raise NotFoundError(f"Image {image_id} not found")
        return image
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("", response_model=List[Image])
async def list_images_new(
    store: Store = Depends(get_current_store),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
):
    """
    List all images for a store
    """
    filters = {"store_id": store.id}
    if status:
        filters["status"] = status
    
    return await image_service.list(
        filters=filters,
        skip=skip,
        limit=limit
    )

@router.get("/stats", response_model=Dict)
async def get_processing_stats(
    store: Store = Depends(get_current_store)
):
    """
    Get image processing statistics
    """
    return await image_service.get_processing_stats(store.id) 