from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
from fastapi import FastAPI, Response
from typing import Dict

class PrometheusMonitoring:
    def __init__(self):
        self.registry = CollectorRegistry()
        
        # Request metrics
        self.request_counter = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.request_latency = Histogram(
            'http_request_duration_seconds',
            'HTTP request latency',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Image processing metrics
        self.processing_queue_size = Gauge(
            'image_processing_queue_size',
            'Number of images in processing queue',
            registry=self.registry
        )
        
        self.processing_duration = Histogram(
            'image_processing_duration_seconds',
            'Image processing duration',
            ['operation_type'],
            registry=self.registry
        )
        
        self.failed_processing = Counter(
            'failed_image_processing_total',
            'Total failed image processing operations',
            ['operation_type', 'error_type'],
            registry=self.registry
        )
        
        # Rate limiting metrics
        self.rate_limit_hits = Counter(
            'rate_limit_hits_total',
            'Total rate limit hits',
            ['shop_id', 'limit_type'],
            registry=self.registry
        )
        
        # CDN metrics
        self.cdn_upload_duration = Histogram(
            'cdn_upload_duration_seconds',
            'CDN upload duration',
            registry=self.registry
        )
        
        self.cdn_errors = Counter(
            'cdn_errors_total',
            'Total CDN operation errors',
            ['operation_type'],
            registry=self.registry
        )

    def track_request(self, method: str, endpoint: str, status: int, duration: float):
        """Track HTTP request metrics"""
        self.request_counter.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_latency.labels(method=method, endpoint=endpoint).observe(duration)

    def update_queue_size(self, size: int):
        """Update image processing queue size"""
        self.processing_queue_size.set(size)

    def track_processing(self, operation_type: str, duration: float):
        """Track image processing metrics"""
        self.processing_duration.labels(operation_type=operation_type).observe(duration)

    def track_processing_error(self, operation_type: str, error_type: str):
        """Track image processing errors"""
        self.failed_processing.labels(
            operation_type=operation_type,
            error_type=error_type
        ).inc()

    def track_rate_limit(self, shop_id: str, limit_type: str):
        """Track rate limit hits"""
        self.rate_limit_hits.labels(shop_id=shop_id, limit_type=limit_type).inc()

    def track_cdn_operation(self, operation_type: str, duration: float, error: bool = False):
        """Track CDN operations"""
        self.cdn_upload_duration.observe(duration)
        if error:
            self.cdn_errors.labels(operation_type=operation_type).inc()

    async def metrics_endpoint(self) -> Response:
        """Generate Prometheus metrics response"""
        return Response(
            generate_latest(self.registry),
            media_type="text/plain"
        )

monitoring = PrometheusMonitoring()

def setup_monitoring(app: FastAPI):
    """Setup monitoring endpoints and middleware"""
    @app.get("/metrics")
    async def metrics():
        return await monitoring.metrics_endpoint() 