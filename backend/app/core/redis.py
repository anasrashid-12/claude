import redis
from typing import Optional, Dict
import os
from app.core.config import get_settings
from app.core.exceptions import RateLimitError
import json
from datetime import datetime, timedelta

settings = get_settings()

class RedisClient:
    _instance = None
    _client: redis.Redis = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            if not os.getenv("TESTING"):
                cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            self._client.ping()
        except Exception as e:
            if not os.getenv("TESTING"):
                raise ConnectionError(f"Failed to connect to Redis: {str(e)}")

    @property
    def client(self) -> redis.Redis:
        return self._client

    def get_cache(self, key: str) -> Optional[dict]:
        if not self._client:
            return None
        try:
            value = self._client.get(key)
            return eval(value) if value else None
        except Exception:
            return None

    def set_cache(self, key: str, value: dict, expire: int = 3600) -> bool:
        if not self._client:
            return False
        try:
            return self._client.setex(key, expire, str(value))
        except Exception:
            return False

    def delete_cache(self, key: str) -> bool:
        if not self._client:
            return False
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
        if not self._client:
            return True
        try:
            current = self._client.get(key)
            if not current:
                if increment:
                    self._client.setex(key, period, 1)
                return True
            
            count = int(current)
            if count >= limit:
                return False
            
            if increment:
                self._client.incr(key)
            return True
        except Exception:
            return True

    def get_lock(self, key: str, expire: int = 30) -> bool:
        if not self._client:
            return True
        try:
            return bool(self._client.set(f"lock:{key}", 1, ex=expire, nx=True))
        except Exception:
            return False

    def release_lock(self, key: str) -> bool:
        if not self._client:
            return True
        try:
            return bool(self._client.delete(f"lock:{key}"))
        except Exception:
            return False

# Create a global instance
redis_client = RedisClient() 