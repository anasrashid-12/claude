from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.queue_manager import QueueManager

router = APIRouter()

class QueueItem(BaseModel):
    id: str
    status: str
    position: int
    created_at: str
    estimated_time: int

class QueueStatus(BaseModel):
    active_jobs: int
    pending_jobs: int
    completed_jobs: int
    failed_jobs: int
    average_processing_time: float

@router.get("/status", response_model=QueueStatus)
async def get_queue_status():
    """
    Get current queue statistics.
    """
    try:
        queue_manager = QueueManager()
        status = await queue_manager.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs", response_model=List[QueueItem])
async def list_queue_jobs():
    """
    List all jobs in the queue.
    """
    try:
        queue_manager = QueueManager()
        jobs = await queue_manager.list_jobs()
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}", response_model=QueueItem)
async def get_queue_job(job_id: str):
    """
    Get details of a specific job in the queue.
    """
    try:
        queue_manager = QueueManager()
        job = await queue_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/jobs/{job_id}")
async def cancel_queue_job(job_id: str):
    """
    Cancel a specific job in the queue.
    """
    try:
        queue_manager = QueueManager()
        success = await queue_manager.cancel_job(job_id)
        if not success:
            raise HTTPException(status_code=404, detail="Job not found or already completed")
        return {"status": "cancelled", "job_id": job_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 