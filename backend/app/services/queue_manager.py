from typing import List, Optional
from datetime import datetime
from app.core.redis import redis_client
from app.core.celery_app import celery_app

class QueueManager:
    def __init__(self):
        self.redis = redis_client
        self.celery = celery_app

    async def get_status(self):
        """Get current queue statistics"""
        active = await self.redis.client.get("queue:active_jobs") or 0
        pending = await self.redis.client.get("queue:pending_jobs") or 0
        completed = await self.redis.client.get("queue:completed_jobs") or 0
        failed = await self.redis.client.get("queue:failed_jobs") or 0
        avg_time = await self.redis.client.get("queue:avg_processing_time") or 0

        return {
            "active_jobs": int(active),
            "pending_jobs": int(pending),
            "completed_jobs": int(completed),
            "failed_jobs": int(failed),
            "average_processing_time": float(avg_time)
        }

    async def list_jobs(self):
        """List all jobs in the queue"""
        jobs = []
        job_keys = await self.redis.client.keys("job:*")
        
        for key in job_keys:
            job_data = await self.redis.client.hgetall(key)
            if job_data:
                jobs.append({
                    "id": key.split(":")[-1],
                    "status": job_data.get("status", "unknown"),
                    "position": int(job_data.get("position", 0)),
                    "created_at": job_data.get("created_at", ""),
                    "estimated_time": int(job_data.get("estimated_time", 0))
                })
        
        return jobs

    async def get_job(self, job_id: str):
        """Get details of a specific job"""
        job_data = await self.redis.client.hgetall(f"job:{job_id}")
        if not job_data:
            return None
            
        return {
            "id": job_id,
            "status": job_data.get("status", "unknown"),
            "position": int(job_data.get("position", 0)),
            "created_at": job_data.get("created_at", ""),
            "estimated_time": int(job_data.get("estimated_time", 0))
        }

    async def cancel_job(self, job_id: str):
        """Cancel a specific job"""
        # Revoke Celery task if exists
        task_id = await self.redis.client.hget(f"job:{job_id}", "task_id")
        if task_id:
            self.celery.control.revoke(task_id, terminate=True)
        
        # Update job status
        await self.redis.client.hset(f"job:{job_id}", "status", "cancelled")
        return True 