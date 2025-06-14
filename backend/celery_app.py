# backend/celery_app.py
from celery import Celery
import os

celery_app = Celery(
    "tasks",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0")
)

@celery_app.task
def process_image_task(task_id, image_bytes, filename, user_id):
    # Placeholder for sending to AI service
    print(f"Processing image {filename} for user {user_id}")
    return True