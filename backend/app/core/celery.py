from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "app",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.image_processing"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3300,  # 55 minutes
    worker_prefetch_multiplier=1,  # One task per worker at a time
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks
    broker_connection_retry_on_startup=True,
)

# Optional: Configure task routing
celery_app.conf.task_routes = {
    "app.tasks.image_processing.*": {"queue": "image_processing"}
}

# Optional: Configure task error handling
celery_app.conf.task_annotations = {
    "*": {
        "rate_limit": "10/m",  # Global rate limit
        "retry_backoff": True,
        "retry_backoff_max": 600,  # Max delay between retries: 10 minutes
        "retry_jitter": True  # Add random jitter to retry delays
    }
} 