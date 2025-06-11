import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_settings
from app.core.database import get_supabase_client
from app.core.redis import RedisClient

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
async def supabase_client():
    client = get_supabase_client()
    yield client

@pytest.fixture
def redis_client():
    client = RedisClient()
    yield client.client
    # Clean up test data
    client.client.flushdb() 