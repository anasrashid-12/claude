#!/bin/bash

# Function to wait for a service to be ready
wait_for_service() {
    local host="$1"
    local port="$2"
    local service="$3"
    
    echo "Waiting for $service to be ready..."
    while ! nc -z "$host" "$port"; do
        sleep 1
    done
    echo "$service is ready!"
}

# Set environment variables
export PYTHONPATH=/app
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# Wait for Redis
wait_for_service "${REDIS_HOST:-redis}" "${REDIS_PORT:-6379}" "Redis"

# Start the application based on the command
case "$1" in
    "api")
        echo "Starting API server..."
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
        ;;
    "worker")
        echo "Starting Celery worker..."
        celery -A app.core.celery worker --loglevel=info --queues=image_processing,shopify_sync
        ;;
    "beat")
        echo "Starting Celery beat..."
        celery -A app.core.celery beat --loglevel=info
        ;;
    "flower")
        echo "Starting Flower monitoring..."
        celery -A app.core.celery flower --port=5555
        ;;
    *)
        echo "Unknown command. Use: api|worker|beat|flower"
        exit 1
        ;;
esac 