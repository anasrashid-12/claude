from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.services.sentry_service import init_sentry
from app.routers.metrics_router import register_metrics
from app.routers.health_router import health_router
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

init_sentry()

def create_app():
    app = FastAPI(
        title="Maxflow AI Image Processor",
        description="Shopify AI Image App - FastAPI Backend",
        version="1.0.0"
    )

    @app.get("/favicon.ico")
    async def favicon():
        return RedirectResponse("https://cdn-icons-png.flaticon.com/512/5977/5977572.png")

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[FRONTEND_URL] if FRONTEND_URL else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(CSPMiddleware)
    app.add_middleware(RateLimitMiddleware)

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = FRONTEND_URL or "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["X-Frame-Options"] = "ALLOWALL"
        response.headers["P3P"] = 'CP="Not used"'
        return response

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        logger.warning(f"HTTP Exception: {exc.detail}")
        return JSONResponse({"error": exc.detail}, status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        logger.warning(f"Validation Error: {exc.errors()}")
        return JSONResponse({"error": "Invalid request"}, status_code=400)

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Unhandled Exception: {exc}")
        return JSONResponse({"error": "Internal Server Error"}, status_code=500)

    # ✅ Include All Routers
    register_metrics(app)
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(upload_router)
    app.include_router(image_router)
    app.include_router(me_router)
    app.include_router(webhook_router)
    app.include_router(fileserve_router)

    logger.info("✅ Backend initialized.")
    return app


app = create_app()
