import redis
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# Create Redis client
redis_client = redis.from_url(
    REDIS_URL,
    password=REDIS_PASSWORD or None,
    decode_responses=True
)

def get_redis():
    """Get Redis client instance."""
    try:
        redis_client.ping()
        return redis_client
    except redis.ConnectionError:
        raise ConnectionError("Could not connect to Redis") 