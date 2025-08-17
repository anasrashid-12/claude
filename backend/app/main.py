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
from app.routers.settings_router import settings_router
from app.routers.credits_router import credits_router
from app.routers.dashboard_stats_router import dashboard_stats_router
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
        version="1.0.0",
    )

    @app.get("/favicon.ico")
    async def favicon():
        return RedirectResponse("https://cdn-icons-png.flaticon.com/512/5977/5977572.png")

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    # --- Core middleware (order matters) ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[FRONTEND_URL] if FRONTEND_URL else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Content-Security-Policy / security hardening
    app.add_middleware(CSPMiddleware)

    # ✅ Production-grade Rate Limiter (dual window + dedupe + overrides)
    app.add_middleware(
        RateLimitMiddleware,
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        # global defaults (burst per second, sustained per minute)
        burst_limit=int(os.getenv("RL_BURST_LIMIT", "10")),
        burst_window_s=int(os.getenv("RL_BURST_WINDOW", "1")),
        sustained_limit=int(os.getenv("RL_SUST_LIMIT", "60")),
        sustained_window_s=int(os.getenv("RL_SUST_WINDOW", "60")),
        # per-path tightening for hot endpoints
        per_path_limits={
            "/upload": (5, 1, 30, 60),             # 5/s burst, 30/min sustained
            "/image": (3, 1, 15, 60),     # example route
        },
        # allow specific shops to bypass limits (CSV env)
        allowlist_shops=set(filter(None, (os.getenv("RL_ALLOWLIST", "").split(",")))),
        exempt_paths={"/health", "/metrics", "/docs", "/openapi.json", "/favicon.ico"},
        exempt_methods={"OPTIONS"},
        jwt_secret=os.getenv("JWT_SECRET", "change_me"),
        # set this if you have a stable user/account id header; otherwise it falls back to shop/ip
        identifier_header=os.getenv("RL_ID_HEADER", ""),
        header_prefix="RateLimit",  # emits RateLimit-Limit/Remaining/Reset
    )

    # Security headers (keep after above)
    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = FRONTEND_URL or "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["P3P"] = 'CP="Not used"'
        return response

    # --- Exception handlers ---
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        logger.warning(f"HTTP Exception: {exc.detail}")
        # 429s from the limiter already include RateLimit headers; preserve them
        headers = getattr(exc, "headers", None)
        return JSONResponse({"error": exc.detail}, status_code=exc.status_code, headers=headers)

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
    app.include_router(settings_router)
    app.include_router(credits_router)
    app.include_router(dashboard_stats_router)

    logger.info("✅ Backend initialized.")
    return app

app = create_app()
