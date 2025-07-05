from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import os

class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        backend_url = os.getenv("BACKEND_URL", "")
        frontend_url = os.getenv("FRONTEND_URL", "")

        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.shopify.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.shopify.com; "
            "font-src 'self' https://cdn.shopify.com data:; "
            "img-src 'self' data: blob: https://cdn.shopify.com; "
            f"connect-src 'self' {frontend_url} {backend_url} https: wss: data: blob:; "
            "frame-ancestors https://admin.shopify.com https://*.myshopify.com; "
            "frame-src https://admin.shopify.com https://*.myshopify.com; "
            "media-src 'self' blob: data:"
        )

        response.headers["Content-Security-Policy"] = csp_policy
        return response
