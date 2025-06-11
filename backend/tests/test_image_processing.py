import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io
from PIL import Image
import numpy as np

def create_test_image():
    """Create a test image for testing"""
    img = Image.fromarray(np.zeros((100, 100, 3), dtype=np.uint8))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def test_process_image_endpoint(client: TestClient, mock_supabase, mock_redis):
    """Test the image processing endpoint"""
    # Create test image
    test_image = create_test_image()
    
    # Mock Supabase response
    mock_supabase.storage.from_().upload.return_value = {"path": "test.png"}
    
    # Test file upload
    files = {"file": ("test.png", test_image, "image/png")}
    data = {"options": '{"quality": 80}'}
    
    response = client.post("/api/v1/images/process", files=files, data=data)
    
    assert response.status_code == 200
    response_data = response.json()
    assert "task_id" in response_data
    assert response_data["status"] == "pending"

def test_process_image_invalid_file(client: TestClient):
    """Test the image processing endpoint with invalid file"""
    # Test with invalid file
    files = {"file": ("test.txt", b"invalid image data", "text/plain")}
    data = {"options": '{"quality": 80}'}
    
    response = client.post("/api/v1/images/process", files=files, data=data)
    
    assert response.status_code == 400
    assert "error" in response.json()

def test_process_image_missing_file(client: TestClient):
    """Test the image processing endpoint without file"""
    data = {"options": '{"quality": 80}'}
    
    response = client.post("/api/v1/images/process", data=data)
    
    assert response.status_code == 422

def test_process_image_invalid_options(client: TestClient):
    """Test the image processing endpoint with invalid options"""
    test_image = create_test_image()
    
    files = {"file": ("test.png", test_image, "image/png")}
    data = {"options": 'invalid json'}
    
    response = client.post("/api/v1/images/process", files=files, data=data)
    
    assert response.status_code == 400
    assert "error" in response.json() 