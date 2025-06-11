from celery import Celery
from .config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.image_processing"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max task runtime
    worker_prefetch_multiplier=1,  # Disable prefetching for long-running tasks
    task_routes={
        "app.tasks.image_processing.*": {"queue": "image_processing"}
    }
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
    worker_max_tasks_per_child=100,
    broker_connection_retry_on_startup=True,
    task_routes={
        "app.tasks.process_image": {"queue": "image_processing"},
        "app.tasks.background_removal": {"queue": "background_removal"},
    },
    task_default_queue="default",
    task_queues={
        "default": {
            "exchange": "default",
            "routing_key": "default",
        },
        "image_processing": {
            "exchange": "image_processing",
            "routing_key": "image_processing",
        },
        "background_removal": {
            "exchange": "background_removal",
            "routing_key": "background_removal",
        },
    },
    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_transport_options={
        'visibility_timeout': 3600,  # 1 hour
    },
    task_annotations={
        '*': {
            'rate_limit': '10/m',  # Global rate limit
            'max_retries': settings.TASK_QUEUE_MAX_RETRIES,
            'retry_backoff': True,
            'retry_backoff_max': 600,  # Maximum retry delay (10 minutes)
            'retry_jitter': True,  # Add random jitter to retry delays
        }
    }
)

# Optional: Configure Flower monitoring
celery_app.conf.update(
    flower_basic_auth=[
        settings.FLOWER_USERNAME + ":" + settings.FLOWER_PASSWORD
    ] if hasattr(settings, "FLOWER_USERNAME") and hasattr(settings, "FLOWER_PASSWORD") else None,
)

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