import time
import redis
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from dotenv import load_dotenv
import os

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

RATE_LIMIT = 60  # 60 requests
WINDOW = 60      # per 60 seconds (1 min)

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        shop = request.query_params.get("shop")

        if not shop:
            raise HTTPException(status_code=400, detail="Missing 'shop' in query params")

        key = f"ratelimit:{shop}"
        current = r.get(key)

        if current and int(current) >= RATE_LIMIT:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # increment count
        pipe = r.pipeline()
        pipe.incr(key, 1)
        pipe.expire(key, WINDOW)
        pipe.execute()

        response = await call_next(request)
        return response
