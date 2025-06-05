from fastapi import Request, HTTPException
from redis import Redis
from os import environ
from datetime import datetime, timedelta
import json

class RateLimiter:
    def __init__(self):
        self.redis = Redis.from_url(
            environ.get('REDIS_URL', 'redis://localhost:6379/0'),
            decode_responses=True
        )
        # Default limits
        self.default_rate_limits = {
            'image_processing': {'calls': 100, 'period': 3600},  # 100 requests per hour
            'product_sync': {'calls': 50, 'period': 3600},      # 50 syncs per hour
            'api_calls': {'calls': 1000, 'period': 3600},       # 1000 API calls per hour
        }

    async def check_rate_limit(self, request: Request, limit_key: str):
        # Get shop ID from session or header
        shop_id = request.headers.get('X-Shop-ID') or 'anonymous'
        
        # Create Redis key for this shop and limit type
        redis_key = f"rate_limit:{shop_id}:{limit_key}"
        
        # Get rate limit settings for this type
        limit_settings = self.default_rate_limits.get(limit_key, {
            'calls': 1000,
            'period': 3600
        })
        
        # Get current timestamp
        now = datetime.now().timestamp()
        
        # Clean up old records
        self.redis.zremrangebyscore(redis_key, 0, now - limit_settings['period'])
        
        # Count requests in the current period
        request_count = self.redis.zcard(redis_key)
        
        if request_count >= limit_settings['calls']:
            # Get the oldest request timestamp
            oldest = float(self.redis.zrange(redis_key, 0, 0, withscores=True)[0][1])
            reset_time = oldest + limit_settings['period']
            
            raise HTTPException(
                status_code=429,
                detail={
                    'error': 'Rate limit exceeded',
                    'reset_at': reset_time,
                    'limit': limit_settings['calls'],
                    'period': limit_settings['period']
                }
            )
        
        # Add current request to the sorted set
        self.redis.zadd(redis_key, {str(now): now})
        
        # Set expiry on the key
        self.redis.expire(redis_key, limit_settings['period'])
        
        return True

    def get_remaining_calls(self, shop_id: str, limit_key: str) -> dict:
        redis_key = f"rate_limit:{shop_id}:{limit_key}"
        now = datetime.now().timestamp()
        
        # Clean up old records
        self.redis.zremrangebyscore(redis_key, 0, now - self.default_rate_limits[limit_key]['period'])
        
        # Count remaining calls
        used_calls = self.redis.zcard(redis_key)
        limit = self.default_rate_limits[limit_key]['calls']
        
        return {
            'remaining': limit - used_calls,
            'limit': limit,
            'reset_at': now + self.default_rate_limits[limit_key]['period']
        }

rate_limiter = RateLimiter() 