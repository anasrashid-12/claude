from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import io

from app.core.security import verify_token
from app.core.database import Database
from app.tasks.image_processing import process_image, remove_background
from app.core.storage import upload_file

router = APIRouter()
security = HTTPBearer()

class ImageProcessingOptions(BaseModel):
    resize: Optional[dict] = None
    brightness: Optional[float] = None
    blur: Optional[int] = None

class ProcessingResponse(BaseModel):
    task_id: str
    status: str
    message: str

@router.post("/images/upload", response_model=ProcessingResponse)
async def upload_image(
    file: UploadFile = File(...),
    options: Optional[str] = Form(None),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Upload and process an image
    """
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        user_id = token_data.get("user_id")
        
        # Read file
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
            
        # Upload original image
        original_filename = f"original_{file.filename}"
        original_url = upload_file(contents, original_filename, file.content_type)
        
        # Create database record
        db = Database()
        image_data = await db.create("images", {
            "user_id": user_id,
            "original_url": original_url,
            "filename": file.filename,
            "status": "processing",
            "created_at": datetime.utcnow().isoformat()
        })
        
        # Start processing task
        task = process_image.delay(
            image_data["id"],
            options if options else {}
        )
        
        return {
            "task_id": task.id,
            "status": "processing",
            "message": "Image upload successful, processing started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/images/{image_id}/background", response_model=ProcessingResponse)
async def remove_image_background(
    image_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Remove background from an image
    """
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        user_id = token_data.get("user_id")
        
        # Check image exists and belongs to user
        db = Database()
        image = await db.get_by_id("images", image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        if image["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        # Start background removal task
        task = remove_background.delay(image_id)
        
        return {
            "task_id": task.id,
            "status": "processing",
            "message": "Background removal started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get the status of a processing task
    """
    try:
        # Verify token
        verify_token(credentials.credentials)
        
        # Get task status
        task = process_image.AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": task.status,
            "result": task.result if task.ready() else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/images")
async def list_images(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    limit: int = 10,
    offset: int = 0
):
    """
    List user's images
    """
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        user_id = token_data.get("user_id")
        
        # Get images
        db = Database()
        result = await db.execute_query(
            "images",
            lambda q: q.select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
        )
        
        return {
            "images": result.data,
            "total": len(result.data),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/images/{image_id}")
async def delete_image(
    image_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Delete an image
    """
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        user_id = token_data.get("user_id")
        
        # Check image exists and belongs to user
        db = Database()
        image = await db.get_by_id("images", image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        if image["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        # Delete from storage
        from app.core.storage import delete_file
        if image.get("original_url"):
            delete_file(f"original_{image['filename']}")
        if image.get("processed_url"):
            delete_file(f"processed_{image_id}.png")
            
        # Delete from database
        await db.delete("images", image_id)
        
        return {"message": "Image deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 