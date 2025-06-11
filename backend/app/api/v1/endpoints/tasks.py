from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.models.task import Task, TaskStatus, TaskType
from app.services.task import TaskService
from app.core.database import get_db
from sqlalchemy.orm import Session
from uuid import UUID

router = APIRouter()

def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)

@router.get("", response_model=List[dict])
async def list_tasks(
    store_id: UUID,
    status: Optional[TaskStatus] = None,
    limit: int = 100,
    offset: int = 0,
    task_service: TaskService = Depends(get_task_service)
):
    """List tasks for a store"""
    try:
        tasks = task_service.list_tasks(
            store_id=store_id,
            status=status,
            limit=limit,
            offset=offset
        )
        return [task.to_dict() for task in tasks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}", response_model=dict)
async def get_task(
    task_id: UUID,
    task_service: TaskService = Depends(get_task_service)
):
    """Get a task by ID"""
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()

@router.post("", response_model=dict)
async def create_task(
    store_id: UUID,
    task_type: TaskType,
    celery_task_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    task_service: TaskService = Depends(get_task_service)
):
    """Create a new task"""
    try:
        task = task_service.create_task(
            store_id=store_id,
            task_type=task_type,
            celery_task_id=celery_task_id,
            metadata=metadata
        )
        return task.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{task_id}", response_model=dict)
async def update_task(
    task_id: UUID,
    status: Optional[TaskStatus] = None,
    progress: Optional[int] = None,
    result: Optional[dict] = None,
    error: Optional[str] = None,
    task_service: TaskService = Depends(get_task_service)
):
    """Update a task"""
    task = task_service.update_task(
        task_id=task_id,
        status=status,
        progress=progress,
        result=result,
        error=error
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()

@router.delete("/{task_id}")
async def delete_task(
    task_id: UUID,
    task_service: TaskService = Depends(get_task_service)
):
    """Delete a task"""
    success = task_service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"} 