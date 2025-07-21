from celery import Celery
import os
from app.logging_config import logger

celery_app = Celery(
    "worker",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL"),
)

celery_app.conf.task_routes = {
    "app.tasks.image_tasks.*": {"queue": "image_queue"},
}

logger.info("✅ Celery app initialized.")

import app.tasks.image_tasks
