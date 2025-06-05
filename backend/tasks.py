from .celery_app import celery_app
import time

@celery_app.task
def slow_add(x, y):
    time.sleep(3)
    return x + y
