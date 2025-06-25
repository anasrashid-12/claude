import redis
import os
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("rate_limiter")

REDIS_URL = os.getenv("REDIS_URL")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

RATE_LIMIT = 60
WINDOW = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        shop = request.query_params.get("shop")
        if not shop:
            return await call_next(request)

        key = f"ratelimit:{shop}"
        current = redis_client.get(key)

        if current and int(current) >= RATE_LIMIT:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        pipe = redis_client.pipeline()
        pipe.incr(key, 1)
        pipe.expire(key, WINDOW)
        pipe.execute()

        return await call_next(request)
