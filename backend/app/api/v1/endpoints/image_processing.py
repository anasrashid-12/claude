from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
from pydantic import BaseModel, HttpUrl
from app.tasks.image_processing import process_image
from celery.result import AsyncResult

router = APIRouter()

class ImageProcessingRequest(BaseModel):
    image_url: HttpUrl
    options: Dict[str, Any]

class TaskResponse(BaseModel):
    task_id: str
    status: str
    progress: Optional[float] = None
    result: Optional[Dict[str, Any]] = None

@router.post("/process", response_model=TaskResponse)
async def create_processing_task(request: ImageProcessingRequest) -> Dict[str, Any]:
    """
    Create a new image processing task
    """
    try:
        # Submit task to Celery
        task = process_image.delay(str(request.image_url), request.options)
        
        return {
            "task_id": task.id,
            "status": task.status,
            "progress": 0,
            "result": None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a processing task
    """
    task = AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": task.status,
        "progress": None,
        "result": None
    }
    
    if task.state == 'PROCESSING':
        response["progress"] = task.info.get('progress', 0)
    elif task.state == 'SUCCESS':
        response["result"] = task.result
    elif task.state == 'FAILURE':
        raise HTTPException(status_code=500, detail=str(task.result))
        
    return response 