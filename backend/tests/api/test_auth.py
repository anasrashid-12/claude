import pytest
from fastapi.testclient import TestClient
from app.models.store import Store

def test_install_endpoint(client: TestClient):
    """Test the install endpoint."""
    response = client.get("/api/v1/auth/install?shop=test-store.myshopify.com")
    assert response.status_code == 200
    data = response.json()
    assert "auth_url" in data
    assert "test-store.myshopify.com" in data["auth_url"]

@pytest.mark.asyncio
async def test_callback_endpoint(client: TestClient):
    """Test the callback endpoint."""
    params = {
        "shop": "test-store.myshopify.com",
        "code": "test_code",
        "timestamp": "1234567890",
        "state": "test_state"
    }
    response = client.get("/api/v1/auth/callback", params=params)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "shop_domain" in data
    assert data["shop_domain"] == "test-store.myshopify.com"

@pytest.mark.asyncio
async def test_uninstall_endpoint(client: TestClient, test_store: Store):
    """Test the uninstall endpoint."""
    response = client.post(
        f"/api/v1/auth/uninstall?shop={test_store.shop_domain}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Store uninstalled successfully"

def test_invalid_shop_domain(client: TestClient):
    """Test install endpoint with invalid shop domain."""
    response = client.get("/api/v1/auth/install?shop=invalid-domain")
    assert response.status_code == 400

def test_missing_shop_parameter(client: TestClient):
    """Test install endpoint without shop parameter."""
    response = client.get("/api/v1/auth/install")
    assert response.status_code == 422  # Validation error 