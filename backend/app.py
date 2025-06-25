from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth_install import auth_install_router
from routers.auth_callback import auth_callback_router
from routers.upload_router import upload_router
from routers.image_routes import image_router
from routers.me_router import me_router
from routers.webhooks_router import webhook_router
from routers.fileserve_router import fileserve_router
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

    app.add_middleware(RateLimitMiddleware)

    app.include_router(auth_install_router)
    app.include_router(auth_callback_router)
    app.include_router(upload_router)
    app.include_router(image_router)
    app.include_router(me_router)
    app.include_router(webhook_router)
    app.include_router(fileserve_router)

    logger.info("Backend app initialized successfully.")
    return app
