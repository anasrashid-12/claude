from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import FastAPI, Response
from typing import Optional
import time

# Request metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests count",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

# Task metrics
TASK_COUNT = Counter(
    "celery_tasks_total",
    "Total Celery tasks",
    ["task_name", "status"]
)

TASK_LATENCY = Histogram(
    "celery_task_duration_seconds",
    "Task execution time in seconds",
    ["task_name"]
)

TASK_QUEUE_SIZE = Gauge(
    "celery_queue_size",
    "Current size of Celery queue",
    ["queue_name"]
)

# Image processing metrics
IMAGE_PROCESSING_COUNT = Counter(
    "image_processing_total",
    "Total image processing operations",
    ["operation_type", "status"]
)

IMAGE_PROCESSING_LATENCY = Histogram(
    "image_processing_duration_seconds",
    "Image processing duration in seconds",
    ["operation_type"]
)

# Rate limiting metrics
RATE_LIMIT_HIT = Counter(
    "rate_limit_hits_total",
    "Total rate limit hits",
    ["endpoint"]
)

def track_request_start_time(request_id: str) -> None:
    """Store request start time"""
    REQUEST_TIMES[request_id] = time.time()

def track_request_end_time(request_id: str, method: str, endpoint: str) -> None:
    """Calculate and record request duration"""
    start_time = REQUEST_TIMES.pop(request_id, None)
    if start_time:
        duration = time.time() - start_time
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

def track_task_execution(task_name: str, duration: float, status: str) -> None:
    """Track Celery task execution"""
    TASK_COUNT.labels(task_name=task_name, status=status).inc()
    TASK_LATENCY.labels(task_name=task_name).observe(duration)

def update_queue_size(queue_name: str, size: int) -> None:
    """Update Celery queue size metric"""
    TASK_QUEUE_SIZE.labels(queue_name=queue_name).set(size)

def track_image_processing(operation: str, duration: float, status: str) -> None:
    """Track image processing metrics"""
    IMAGE_PROCESSING_COUNT.labels(operation_type=operation, status=status).inc()
    IMAGE_PROCESSING_LATENCY.labels(operation_type=operation).observe(duration)

def track_rate_limit(endpoint: str) -> None:
    """Track rate limit hits"""
    RATE_LIMIT_HIT.labels(endpoint=endpoint).inc()

async def metrics_endpoint() -> Response:
    """Endpoint to expose metrics"""
    return Response(
        generate_latest(),
        media_type="text/plain"
    )

def setup_monitoring(app: FastAPI) -> None:
    """Setup monitoring for the FastAPI app"""
    @app.middleware("http")
    async def monitoring_middleware(request, call_next):
        # Track request timing
        request_id = str(time.time())
        track_request_start_time(request_id)
        
        response = await call_next(request)
        
        # Record metrics
        track_request_end_time(request_id, request.method, request.url.path)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        return response

    # Add metrics endpoint
    app.add_route("/metrics", metrics_endpoint) 