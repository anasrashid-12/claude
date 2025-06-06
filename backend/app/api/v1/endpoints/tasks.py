from fastapi import APIRouter, HTTPException, Depends, Query
from app.services.task import task_service
from app.models.task import Task, TaskType
from app.models.store import Store
from app.core.exceptions import NotFoundError, ValidationError
from typing import List, Optional, Dict
from app.api.deps import get_current_store

router = APIRouter()

@router.get("", response_model=List[Task])
async def list_tasks(
    store: Store = Depends(get_current_store),
    skip: int = 0,
    limit: int = 100,
    task_type: Optional[TaskType] = None,
    status: Optional[str] = None
):
    """
    List tasks for a store
    """
    filters = {"store_id": store.id}
    if task_type:
        filters["task_type"] = task_type
    if status:
        filters["status"] = status
    
    return await task_service.list(
        filters=filters,
        skip=skip,
        limit=limit
    )

@router.get("/active", response_model=List[Task])
async def get_active_tasks(
    store: Store = Depends(get_current_store),
    task_type: Optional[TaskType] = None
):
    """
    Get active tasks for a store
    """
    return await task_service.get_active_tasks(store.id, task_type)

@router.get("/stats", response_model=Dict)
async def get_task_stats(
    store: Store = Depends(get_current_store)
):
    """
    Get task statistics for a store
    """
    return await task_service.get_task_stats(store.id)

@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    store: Store = Depends(get_current_store)
):
    """
    Get task by ID
    """
    try:
        task = await task_service.get(task_id)
        if task.store_id != store.id:
            raise NotFoundError("Task not found")
        return task
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{task_id}")
async def cancel_task(
    task_id: int,
    store: Store = Depends(get_current_store),
    terminate: bool = False
):
    """
    Cancel a task
    """
    try:
        task = await task_service.get(task_id)
        if task.store_id != store.id:
            raise NotFoundError("Task not found")
        
        success = task_service.revoke_task(task.celery_task_id, terminate)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to cancel task")
        
        return {"message": "Task cancelled successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) 