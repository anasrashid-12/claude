# backend/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes.auth import auth_router
from routes.upload import upload_router
from routers.image_routes import image_router
from middleware.rate_limiter import RateLimitMiddleware
from logging_config import logger

def create_app():
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router, prefix="/auth")
    app.include_router(upload_router, prefix="/upload")
    app.include_router(image_router, prefix="/image")
    app.add_middleware(RateLimitMiddleware)
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    logger.info("Backend app initialized successfully.")
    return app
