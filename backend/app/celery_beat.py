# celery_beat.py
from app.celery_app import celery_app
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "poll-processing-images-every-minute": {
        "task": "app.tasks.image_tasks.poll_all_processing_images",
        "schedule": crontab(minute="*/5"),  # every 1 minute
    },
}

celery_app.conf.timezone = "UTC"
