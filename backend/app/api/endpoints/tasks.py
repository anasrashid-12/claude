from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from app.services.task import task_service
from app.models.task import TaskType, TaskStatus
from app.core.auth import get_current_store
from app.tasks.image_processing import process_image, bulk_process

router = APIRouter()

@router.post("/tasks/image/{image_id}")
async def create_image_task(
    image_id: int,
    store: Dict[str, Any] = Depends(get_current_store)
) -> Dict[str, Any]:
    """Create a new image processing task"""
    # Create async task
    task = process_image.delay(image_id)
    
    # Create task record
    db_task = task_service.create(
        task_id=task.id,
        task_type=TaskType.IMAGE_PROCESSING,
        store_id=store["id"],
        params={"image_id": image_id}
    )
    
    return {
        "task_id": db_task.id,
        "status": db_task.status,
        "type": db_task.task_type
    }

@router.post("/tasks/bulk")
async def create_bulk_task(
    image_ids: List[int],
    store: Dict[str, Any] = Depends(get_current_store)
) -> Dict[str, Any]:
    """Create a new bulk processing task"""
    # Create async task
    task = bulk_process.delay(image_ids)
    
    # Create task record
    db_task = task_service.create(
        task_id=task.id,
        task_type=TaskType.BULK_PROCESSING,
        store_id=store["id"],
        params={"image_ids": image_ids}
    )
    
    return {
        "task_id": db_task.id,
        "status": db_task.status,
        "type": db_task.task_type
    }

@router.get("/tasks/{task_id}")
async def get_task(
    task_id: str,
    store: Dict[str, Any] = Depends(get_current_store)
) -> Dict[str, Any]:
    """Get task status"""
    task = task_service.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.store_id != store["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this task")
    
    celery_status = task_service.get_task_status(task_id)
    
    return {
        "task_id": task.id,
        "status": task.status,
        "type": task.task_type,
        "result": task.result,
        "error": task.error_message,
        "celery_status": celery_status
    }

@router.get("/tasks")
async def list_tasks(
    store: Dict[str, Any] = Depends(get_current_store),
    status: TaskStatus = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """List tasks for a store"""
    tasks = task_service.list_by_store(
        store_id=store["id"],
        status=status,
        limit=limit,
        offset=offset
    )
    
    return [{
        "task_id": task.id,
        "status": task.status,
        "type": task.task_type,
        "result": task.result,
        "error": task.error_message,
        "created_at": task.created_at,
        "completed_at": task.completed_at
    } for task in tasks]

@router.delete("/tasks/{task_id}")
async def cancel_task(
    task_id: str,
    store: Dict[str, Any] = Depends(get_current_store)
) -> Dict[str, str]:
    """Cancel a running task"""
    task = task_service.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.store_id != store["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this task")
    
    if task_service.revoke_task(task_id, terminate=True):
        return {"status": "Task cancelled successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to cancel task") 