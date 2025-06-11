import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.core.config import get_settings

settings = get_settings()

@pytest.mark.api
def test_process_image_endpoint(client: TestClient):
    """Test the image processing endpoint"""
    test_image = b"fake image data"
    files = {"file": ("test.jpg", test_image, "image/jpeg")}
    
    response = client.post(
        f"{settings.API_V1_STR}/images/process",
        files=files,
        data={"options": '{"quality": 80}'}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"

@pytest.mark.api
def test_process_image_invalid_file(client: TestClient):
    """Test the image processing endpoint with invalid file"""
    response = client.post(
        f"{settings.API_V1_STR}/images/process",
        files={},
        data={"options": '{"quality": 80}'}
    )
    
    assert response.status_code == 422

@pytest.mark.api
@patch("app.services.image_processor.ImageProcessor.process_image")
async def test_process_image_service_error(mock_process, client: TestClient):
    """Test handling of processing service errors"""
    mock_process.side_effect = Exception("Processing failed")
    
    test_image = b"fake image data"
    files = {"file": ("test.jpg", test_image, "image/jpeg")}
    
    response = client.post(
        f"{settings.API_V1_STR}/images/process",
        files=files,
        data={"options": '{"quality": 80}'}
    )
    
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data 