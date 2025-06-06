from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
import os
from .api.routes import shopify
from .core.redis_client import get_redis
from .database import Database
from prometheus_client import make_asgi_app
from app.core.config import settings
from app.api.v1.router import api_router
from app.core.exceptions import AppException

# Load environment variables
load_dotenv()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="AI Image Processing API for Shopify stores",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Error handling middleware
@app.middleware("http")
async def errors_handling(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal server error",
                "detail": str(exc)
            }
        )

# Include routers
app.include_router(shopify.router)
app.include_router(api_router, prefix="/api/v1")

# Exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.get("/")
async def root():
    return {"status": "healthy", "service": "shopify-ai-image-processor"}

@app.get("/health")
async def health_check():
    try:
        # Check database connection
        db = Database()
        await db.client.from_('stores').select('*').limit(1).execute()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    try:
        # Check Redis connection
        redis = get_redis()
        redis.ping()
        redis_status = "connected"
    except Exception as e:
        redis_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "services": {
            "database": db_status,
            "redis": redis_status,
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 