from datetime import datetime, timedelta
from app.core.redis import redis_client
from app.core.celery_app import celery_app
import psutil

class StatsManager:
    def __init__(self):
        self.redis = redis_client
        self.celery = celery_app

    async def get_processing_stats(self, start_date: datetime, end_date: datetime):
        """Get image processing statistics for a time period"""
        total = await self.redis.client.get("stats:total_processed") or 0
        success = await self.redis.client.get("stats:success_count") or 0
        total_time = await self.redis.client.get("stats:total_processing_time") or 0
        storage = await self.redis.client.get("stats:total_storage") or 0
        hourly = await self.redis.client.get("stats:images_per_hour") or 0

        total = int(total)
        success_rate = (int(success) / total * 100) if total > 0 else 0
        avg_time = float(total_time) / total if total > 0 else 0

        return {
            "total_processed": total,
            "success_rate": round(success_rate, 2),
            "average_processing_time": round(avg_time, 2),
            "total_storage_used": int(storage),
            "images_per_hour": float(hourly)
        }

    async def get_resource_stats(self):
        """Get current system resource usage"""
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "queue_size": await self.redis.client.get("queue:total_jobs") or 0,
            "active_workers": len(self.celery.control.inspect().active() or {})
        }

    async def get_error_stats(self, start_date: datetime, end_date: datetime):
        """Get error statistics for a time period"""
        error_keys = await self.redis.client.keys("error:*")
        error_stats = {}
        
        for key in error_keys:
            error_type = key.split(":")[-1]
            count = await self.redis.client.get(key) or 0
            error_stats[error_type] = int(count)
            
        return {
            "total_errors": sum(error_stats.values()),
            "error_types": error_stats,
            "time_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        } 