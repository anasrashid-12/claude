from celery import Celery
import os
from app.logging_config import logger

# Create the Celery app
celery_app = Celery(
    "worker",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL"),
)

# Route image tasks to a specific queue
celery_app.conf.task_routes = {
    "app.tasks.image_tasks.submit_image_task": {"queue": "image_queue"},
    "app.tasks.image_tasks.poll_all_processing_images": {"queue": "polling_queue"},
}

# Optional: enable UTC & serializer settings
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)

logger.info("✅ Celery app initialized.")

# Import tasks so Celery can register them
import app.tasks.image_tasks
