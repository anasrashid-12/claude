from celery import Celery
from os import environ

# Configure Celery with Redis
celery_app = Celery(
    'shopify_image_processor',
    broker=environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
    backend=environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2'),
)

# Configure Celery settings
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max task runtime
    worker_prefetch_multiplier=1,  # One task per worker at a time
    task_routes={
        'tasks.process_image': {'queue': 'image_processing'},
        'tasks.sync_products': {'queue': 'shopify_sync'},
    }
)
