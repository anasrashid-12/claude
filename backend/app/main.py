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

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Shopify AI Image Processor",
    description="API for processing Shopify product images using AI",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
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