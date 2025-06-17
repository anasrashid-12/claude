# backend/middleware/rate_limiter.py
import time
import redis
import os
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("rate_limiter")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

RATE_LIMIT = 60  # 60 requests
WINDOW = 60      # per 60 seconds (1 minute)

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        shop = request.query_params.get("shop")

        # Skip rate limiting for non-shop routes like /me, /auth, etc.
        if not shop:
            return await call_next(request)

        key = f"ratelimit:{shop}"

        try:
            current = r.get(key)
            if current and int(current) >= RATE_LIMIT:
                logger.warning(f"[RateLimit] Exceeded: shop={shop}, count={current}")
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            pipe = r.pipeline()
            pipe.incr(key, 1)
            pipe.expire(key, WINDOW)
            pipe.execute()

        except redis.exceptions.RedisError as e:
            logger.error(f"[RateLimit] Redis error: {e}")
            # Fail open — allow request if Redis is down
            return await call_next(request)

        return await call_next(request)
