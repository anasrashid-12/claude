#!/bin/bash

# Start Celery in background
celery -A app.celery_app.celery_app worker --loglevel=info -Q image_queue &

# Start FastAPI server
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
