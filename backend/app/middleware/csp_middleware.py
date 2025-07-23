from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import os

class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        backend_url = os.getenv("BACKEND_URL", "").rstrip("/")
        frontend_url = os.getenv("FRONTEND_URL", "").rstrip("/")
        supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")

        # Extract hostnames for connect-src
        from urllib.parse import urlparse
        supabase_host = urlparse(supabase_url).hostname or ""
        ws_supabase = f"wss://{supabase_host}" if supabase_host else ""

        csp_policy = (
            "default-src 'self' https: data: blob:; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; "
            "style-src 'self' 'unsafe-inline' https:; "
            "img-src 'self' data: blob: https:; "
            "font-src 'self' https: data:; "
            f"connect-src 'self' {frontend_url} {backend_url} {supabase_url} {ws_supabase} "
            "https://*.shopify.com https://cdn.shopify.com wss://*.supabase.co blob: data:; "
            "media-src 'self' blob: data:; "
            "worker-src 'self' blob:; "
            "frame-ancestors https://admin.shopify.com https://*.myshopify.com; "
            "frame-src https://admin.shopify.com https://*.myshopify.com; "
            "object-src 'none';"
        )

        response.headers["Content-Security-Policy"] = csp_policy
        return response
