from celery import Celery
import os
from logging_config import logger

celery = Celery(
    "worker",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0"),
)

import tasks.image_tasks

celery.conf.task_routes = {
    "tasks.image_tasks.*": {"queue": "image_queue"},
}

logger.info("Celery app initialized.")
