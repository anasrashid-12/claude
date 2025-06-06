import redis
from app.core.config import settings
from app.core.exceptions import RateLimitError
from typing import Optional
import json
from datetime import datetime, timedelta

class RedisClient:
    _instance = None
    _client: redis.Redis = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            self._client = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            self._client.ping()  # Test connection
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {str(e)}")

    @property
    def client(self) -> redis.Redis:
        if not self._client:
            self._initialize()
        return self._client

    def get_cache(self, key: str) -> Optional[dict]:
        """Get cached data"""
        try:
            data = self._client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None

    def set_cache(self, key: str, value: dict, expire: int = 3600) -> bool:
        """Set cached data with expiration in seconds"""
        try:
            return self._client.setex(
                key,
                expire,
                json.dumps(value)
            )
        except Exception:
            return False

    def delete_cache(self, key: str) -> bool:
        """Delete cached data"""
        try:
            return bool(self._client.delete(key))
        except Exception:
            return False

    def check_rate_limit(
        self,
        key: str,
        limit: int,
        period: int = 60,
        increment: bool = True
    ) -> bool:
        """
        Check if rate limit is exceeded
        Args:
            key: Rate limit key (e.g., "user:123:api")
            limit: Maximum number of requests
            period: Time period in seconds
            increment: Whether to increment the counter
        Returns:
            bool: True if limit is not exceeded
        """
        try:
            pipeline = self._client.pipeline()
            pipeline.get(key)
            if increment:
                pipeline.incr(key)
                pipeline.expire(key, period)
            result = pipeline.execute()

            current = int(result[0]) if result[0] else 0
            if not increment:
                return current < limit

            if current > limit:
                raise RateLimitError(
                    f"Rate limit exceeded. Try again in {self._client.ttl(key)} seconds."
                )
            return True
        except RateLimitError:
            raise
        except Exception as e:
            # Log error but don't block the request
            print(f"Rate limit check failed: {str(e)}")
            return True

    def get_lock(self, key: str, expire: int = 30) -> bool:
        """Get distributed lock"""
        return bool(self._client.set(
            f"lock:{key}",
            datetime.utcnow().isoformat(),
            ex=expire,
            nx=True
        ))

    def release_lock(self, key: str) -> bool:
        """Release distributed lock"""
        return bool(self._client.delete(f"lock:{key}"))

# Create a global instance
redis_client = RedisClient() 