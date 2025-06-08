from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.image_processor import ImageProcessor
from app.core.config import settings
from app.services.image import image_service
from app.models.image import Image, ProcessingType, ProcessingStatus
from app.models.store import Store
from app.core.exceptions import NotFoundError, ValidationError
from app.api.deps import get_current_store
from app.core.security import get_current_user
from app.schemas.image import ImageCreate, ImageResponse, ImageUpdate
from app.crud.image import image_crud
from app.tasks.image_processing import process_image, bulk_process

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
    """Request model for image processing"""
    product_id: str
    image_id: str
    original_url: str
    processing_types: List[ProcessingType]
    processing_options: Optional[Dict] = None
    position: Optional[int] = None
    alt_text: Optional[str] = None

class BulkProcessRequest(BaseModel):
    """Request model for bulk processing"""
    images: List[ProcessImageRequest]

@router.post("/", response_model=ImageResponse)
async def create_image(
    *,
    file: UploadFile = File(...),
    product_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    processing_options: Optional[dict] = None
) -> ImageResponse:
    """
    Upload and process a new image.
    """
    # Validate file type and size
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create image record
    image_in = ImageCreate(
        product_id=product_id,
        original_url="",  # Will be updated after upload
        auth_user_id=current_user["id"],
        processing_options=processing_options or {}
    )
    
    image = await image_crud.create(obj_in=image_in)
    
    # Start processing in background
    background_tasks.add_task(
        process_image,
        image_id=image.id,
        file=file,
        processing_options=processing_options
    )
    
    return image

@router.get("/", response_model=List[ImageResponse])
async def list_images(
    *,
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[str] = None
) -> List[ImageResponse]:
    """
    Retrieve all images for the current user.
    """
    filters = {
        "auth_user_id": current_user["id"]
    }
    if product_id:
        filters["product_id"] = product_id
        
    images = await image_crud.get_multi(
        skip=skip, limit=limit, filters=filters
    )
    return images

@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(
    *,
    current_user: dict = Depends(get_current_user),
    image_id: str
) -> ImageResponse:
    """
    Get image by ID.
    """
    image = await image_crud.get(id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    if image.auth_user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return image

@router.put("/{image_id}", response_model=ImageResponse)
async def update_image(
    *,
    current_user: dict = Depends(get_current_user),
    image_id: str,
    image_in: ImageUpdate
) -> ImageResponse:
    """
    Update image.
    """
    image = await image_crud.get(id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    if image.auth_user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    image = await image_crud.update(id=image_id, obj_in=image_in)
    return image

@router.delete("/{image_id}")
async def delete_image(
    *,
    current_user: dict = Depends(get_current_user),
    image_id: str
):
    """
    Delete image.
    """
    image = await image_crud.get(id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    if image.auth_user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    await image_crud.remove(id=image_id)
    return {"status": "success"}

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
    Process a single image with specified operations
    """
    try:
        # Create task
        task = process_image.delay(
            data.image_id,
            data.processing_types,
            data.processing_options
        )

        # Return initial response
        return {
            "id": data.image_id,
            "product_id": data.product_id,
            "original_url": data.original_url,
            "status": ProcessingStatus.PENDING,
            "task_id": task.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk", response_model=List[Image])
async def bulk_process_images(
    data: BulkProcessRequest,
    store: Store = Depends(get_current_store)
):
    """
    Process multiple images in bulk
    """
    try:
        # Extract image IDs and processing types
        image_ids = [img.image_id for img in data.images]
        processing_types = data.images[0].processing_types  # Assume same processing for all
        processing_options = data.images[0].processing_options

        # Create bulk processing task
        task = bulk_process.delay(
            image_ids,
            processing_types,
            processing_options
        )

        # Return initial response for all images
        return [
            {
                "id": img.image_id,
                "product_id": img.product_id,
                "original_url": img.original_url,
                "status": ProcessingStatus.PENDING,
                "task_id": task.id
            }
            for img in data.images
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/product/{product_id}", response_model=List[Image])
async def get_product_images(
    product_id: str,
    store: Store = Depends(get_current_store)
):
    """
    Get all images for a specific product
    """
    try:
        processor = ImageProcessor()
        images = await processor.get_by_product(store.id, product_id)
        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{image_id}", response_model=Image)
async def get_image_new(
    image_id: str,
    store: Store = Depends(get_current_store)
):
    """
    Get details of a specific image
    """
    try:
        processor = ImageProcessor()
        image = await processor.get_by_image_id(store.id, image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        return image
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[Image])
async def list_images_new(
    store: Store = Depends(get_current_store),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
):
    """
    List all images for the current store
    """
    try:
        processor = ImageProcessor()
        filters = {"store_id": store.id}
        if status:
            filters["status"] = status
        images = await processor.list_images(filters, skip, limit)
        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=Dict)
async def get_processing_stats(
    store: Store = Depends(get_current_store)
):
    """
    Get image processing statistics for the store
    """
    try:
        processor = ImageProcessor()
        stats = await processor.get_processing_stats(store.id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 