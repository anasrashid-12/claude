import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.database import db
from app.models.store import Store, StoreCreate
from app.services.store import store_service
import asyncio
from typing import Generator, AsyncGenerator

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def client() -> Generator:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session")
async def test_db() -> AsyncGenerator:
    """Create a test database connection."""
    # Here you would typically set up a test database
    # For now, we'll use the same database but with test_ prefix tables
    yield db

@pytest.fixture(scope="function")
async def test_store(test_db: db) -> AsyncGenerator[Store, None]:
    """Create a test store."""
    store_data = StoreCreate(
        shop_domain="test-store.myshopify.com",
        access_token="test_token",
        is_active=True
    )
    store = await store_service.create(store_data)
    yield store
    # Cleanup
    await store_service.delete(store.id)

@pytest.fixture(scope="session")
def test_headers(test_store: Store) -> dict:
    """Create test headers with store authentication."""
    return {
        "X-Shopify-Shop-Domain": test_store.shop_domain,
        "X-Shopify-Access-Token": test_store.access_token
    } 