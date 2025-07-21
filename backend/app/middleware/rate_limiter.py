# rate_limiter.py (Final Suggested Version)

import redis
import os
import logging
import asyncio
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from redis.exceptions import RedisError

logger = logging.getLogger("rate_limiter")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET = os.getenv("JWT_SECRET", "maxflow_secret")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

RATE_LIMIT = int(os.getenv("RATE_LIMIT", "60"))
WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        shop = request.query_params.get("shop")

        if not shop:
            session = request.cookies.get("session")
            if session:
                try:
                    payload = jwt.decode(session, JWT_SECRET, algorithms=["HS256"])
                    shop = payload.get("shop")
                except jwt.ExpiredSignatureError:
                    logger.warning("JWT expired.")
                except jwt.DecodeError as e:
                    logger.warning(f"JWT decode error: {e}")

        if not shop:
            return await call_next(request)

        key = f"ratelimit:{shop}"

        try:
            current = await asyncio.to_thread(redis_client.get, key)
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
            return await call_next(request)

        if current and int(current) >= RATE_LIMIT:
            logger.warning(f"🚫 Rate limit exceeded for shop: {shop}")
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        await asyncio.to_thread(self.increment_with_expiry, key)
        return await call_next(request)

    @staticmethod
    def increment_with_expiry(key: str):
        try:
            with redis_client.pipeline() as pipe:
                pipe.incr(key, 1)
                pipe.expire(key, WINDOW)
                pipe.execute()
        except RedisError as e:
            logger.error(f"Redis pipeline error: {e}")
