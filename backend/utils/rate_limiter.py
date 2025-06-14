# backend/utils/rate_limiter.py
import redis
from fastapi import Request, HTTPException
from functools import wraps
import os

r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

def rate_limiter(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        user = kwargs.get("user")
        key = f"rate:{user['user_id']}"
        if r.incr(key) > 10:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        r.expire(key, 60)
        return await func(*args, **kwargs)
    return wrapper
