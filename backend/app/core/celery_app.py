from celery import Celery
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# Create Celery instance
celery_app = Celery(
    "shopify_image_processor",
    broker=REDIS_URL,
    backend=REDIS_URL,
    broker_connection_retry_on_startup=True
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    worker_max_tasks_per_child=100,
    broker_connection_max_retries=None,
)

# Optional: Configure task routes
celery_app.conf.task_routes = {
    "app.tasks.image_processing.*": {"queue": "image_processing"},
    "app.tasks.shopify.*": {"queue": "shopify_sync"},
} 