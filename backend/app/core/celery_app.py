from celery import Celery
from .config import settings

celery_app = Celery(
    "shopify_ai_image_processor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
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

# Define task routes
celery_app.conf.task_routes = {
    "app.tasks.image_processing.*": {"queue": "image_processing"}
}

# Define task queues
celery_app.conf.task_queues = {
    "image_processing": {
        "exchange": "image_processing",
        "routing_key": "image_processing",
    }
}

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])

# Optional: Add periodic tasks
celery_app.conf.beat_schedule = {
    # Example periodic task
    # 'cleanup-old-images': {
    #     'task': 'app.tasks.cleanup.cleanup_old_images',
    #     'schedule': 3600.0,  # Run every hour
    # },
}

# Additional settings
celery_app.conf.update(
    task_default_queue="image_processing",
    task_default_exchange="image_processing",
    task_default_routing_key="image_processing",
) 