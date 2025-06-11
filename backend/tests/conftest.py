import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Add the application root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set testing environment
os.environ["TESTING"] = "1"

# Test configuration
test_settings = {
    "PROJECT_NAME": "Shopify AI Image App Test",
    "VERSION": "1.0.0",
    "API_V1_STR": "/api/v1",
    "DEBUG": True,
    "SUPABASE_URL": "http://localhost:54321",
    "SUPABASE_KEY": "test-key",
    "SUPABASE_JWT_SECRET": "test-secret",
    "SUPABASE_DB_HOST": "localhost",
    "SUPABASE_DB_PORT": 5432,
    "SUPABASE_DB_NAME": "postgres",
    "SUPABASE_DB_USER": "postgres",
    "SUPABASE_DB_PASSWORD": "postgres",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": 6379,
    "REDIS_DB": 1,
    "STORAGE_PROVIDER": "local",
    "STORAGE_PATH": "./test_storage",
    "STORAGE_PUBLIC_URL": "http://localhost:8000/storage",
    "JWT_SECRET_KEY": "test-jwt-secret-key",
    "JWT_ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 60,
    "SHOPIFY_API_KEY": "test-api-key",
    "SHOPIFY_API_SECRET": "test-api-secret",
    "SHOPIFY_APP_URL": "http://localhost:3000",
    "SHOPIFY_SCOPES": "write_products,write_files,read_files"
}

# Apply test settings
for key, value in test_settings.items():
    os.environ[key] = str(value)

# Mock external dependencies
mock_supabase = MagicMock()
mock_redis = MagicMock()

# Patch dependencies before importing app
with patch('app.core.database.get_supabase_client', return_value=mock_supabase), \
     patch('app.core.redis.RedisClient', return_value=mock_redis):
    from app.main import app
    from app.core.config import get_settings

@pytest.fixture
def test_app():
    return app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

@pytest.fixture
def settings():
    return get_settings()

@pytest.fixture
def mock_supabase():
    return mock_supabase

@pytest.fixture
def mock_redis():
    return mock_redis

@pytest.fixture
async def supabase_client():
    client = get_supabase_client()
    yield client

@pytest.fixture
def redis_client():
    client = RedisClient()
    yield client.client
    # Clean up test data
    client.client.flushdb() 