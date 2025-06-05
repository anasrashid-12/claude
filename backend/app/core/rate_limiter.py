from fastapi import Request, HTTPException
from redis import Redis
import time
from typing import Optional
from .redis_client import get_redis

class RateLimiter:
    def __init__(
        self,
        times: int = 60,  # Number of requests
        seconds: int = 60,  # Time window in seconds
        key_prefix: str = "rate_limit"
    ):
        self.times = times
        self.seconds = seconds
        self.key_prefix = key_prefix
        self.redis: Optional[Redis] = None

    def _get_redis(self) -> Redis:
        if not self.redis:
            self.redis = get_redis()
        return self.redis

    def _get_key(self, key: str) -> str:
        return f"{self.key_prefix}:{key}"

    async def is_rate_limited(self, key: str) -> bool:
        redis = self._get_redis()
        key = self._get_key(key)
        
        # Get the current count
        current = redis.get(key)
        
        if current is None:
            # First request, set expiry
            pipeline = redis.pipeline()
            pipeline.set(key, 1)
            pipeline.expire(key, self.seconds)
            pipeline.execute()
            return False
            
        current = int(current)
        if current >= self.times:
            return True
            
        # Increment the counter
        redis.incr(key)
        return False

async def rate_limit_by_ip(
    request: Request,
    times: int = 60,
    seconds: int = 60
):
    limiter = RateLimiter(times=times, seconds=seconds)
    client_ip = request.client.host
    
    if await limiter.is_rate_limited(client_ip):
        raise HTTPException(
            status_code=429,
            detail={
                "message": "Too many requests",
                "retry_after": seconds
            }
        ) 