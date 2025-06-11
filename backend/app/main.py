from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from dotenv import load_dotenv
import os
import logging

from app.core.config import settings, get_settings
from app.core.supabase import SupabaseClient
from app.core.exceptions import AppException
from app.core.middleware import RequestLoggingMiddleware, RateLimitMiddleware
from app.api.v1.router import api_router
from app.core.storage import mount_storage
from app.api.v1.auth import shopify
from app.core.celery_app import celery_app
from app.core.security import verify_token
from app.core.database import get_supabase_client, init_database
from app.api.v1.endpoints import image_processing
from app.core.monitoring.prometheus import setup_monitoring

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    Shopify AI Image Processing App API
    
    This API provides endpoints for:
    * Image processing and optimization
    * Background removal
    * Bulk image operations
    * Task management and monitoring
    * Store management and authentication
    """,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Security
security = HTTPBearer()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Mount storage directory for serving files
if settings.STORAGE_PROVIDER == "local":
    mount_storage(app)

# Add monitoring
setup_monitoring(app)

# Error handling middleware
@app.middleware("http")
async def errors_handling(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(
    shopify.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["auth"]
)
app.include_router(
    image_processing.router,
    prefix=f"{settings.API_V1_STR}/image-processing",
    tags=["image-processing"]
)

# Exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.get("/")
async def root():
    """Root endpoint returning API status"""
    return {"status": "ok", "version": settings.VERSION}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.DEBUG and "development" or "production"
    }

# Protected route example
@app.get("/protected")
async def protected_route(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Test endpoint for authentication"""
    return {"status": "authenticated", "token": credentials.credentials}

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting up API server...")
    try:
        # Initialize database connection
        await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    # Initialize monitoring
    setup_monitoring(app)
    logger.info("API server started successfully")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 