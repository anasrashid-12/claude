from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.services.stats_manager import StatsManager

router = APIRouter()

class ProcessingStats(BaseModel):
    total_processed: int
    success_rate: float
    average_processing_time: float
    total_storage_used: int
    images_per_hour: float

class ResourceStats(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    queue_size: int
    active_workers: int

@router.get("/processing", response_model=ProcessingStats)
async def get_processing_stats(
    start_date: datetime = None,
    end_date: datetime = None
):
    """
    Get image processing statistics for a given time period.
    If no dates provided, returns stats for the last 24 hours.
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=1)
        if not end_date:
            end_date = datetime.now()
            
        stats_manager = StatsManager()
        stats = await stats_manager.get_processing_stats(start_date, end_date)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resources", response_model=ResourceStats)
async def get_resource_stats():
    """
    Get current system resource usage statistics.
    """
    try:
        stats_manager = StatsManager()
        stats = await stats_manager.get_resource_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/errors")
async def get_error_stats(
    start_date: datetime = None,
    end_date: datetime = None
):
    """
    Get error statistics for a given time period.
    If no dates provided, returns stats for the last 24 hours.
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=1)
        if not end_date:
            end_date = datetime.now()
            
        stats_manager = StatsManager()
        stats = await stats_manager.get_error_stats(start_date, end_date)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 