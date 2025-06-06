#!/bin/bash

# Start Celery worker for image processing
celery -A app.core.celery worker \
    --loglevel=info \
    --concurrency=2 \
    --queues=image_processing \
    --hostname=worker@%h \
    --pool=prefork 