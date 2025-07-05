from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth_router import auth_router
from app.routers.upload_router import upload_router
from app.routers.image_router import image_router
from app.routers.me_router import me_router
from app.routers.webhooks_router import webhook_router
from app.routers.fileserve_router import fileserve_router

from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.csp_middleware import CSPMiddleware

from app.logging_config import logger

import os

FRONTEND_URL = os.getenv("FRONTEND_URL")


def create_app():
    app = FastAPI()

    @app.get("/favicon.ico")
    async def favicon():
        return RedirectResponse("https://cdn-icons-png.flaticon.com/512/5977/5977572.png")

    # ✅ CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[FRONTEND_URL] if FRONTEND_URL else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ✅ Add CSP Middleware
    app.add_middleware(CSPMiddleware)

    # ✅ Rate Limit Middleware
    app.add_middleware(RateLimitMiddleware)

    # ✅ Security Headers Middleware (for iframe + cookie support)
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = FRONTEND_URL or "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["X-Frame-Options"] = "ALLOWALL"
        response.headers["P3P"] = 'CP="Not used"'
        return response

    # ✅ Include Routers
    app.include_router(auth_router)
    app.include_router(upload_router)
    app.include_router(image_router)
    app.include_router(me_router)
    app.include_router(webhook_router)
    app.include_router(fileserve_router)

    logger.info("✅ Backend initialized successfully.")
    return app


app = create_app()
