import httpx
import pytest
from pathlib import Path
import os
import asyncio
from PIL import Image
import io

# Configuration
AI_SERVICE_URL = "http://localhost:8001"
TEST_IMAGE_PATH = Path(__file__).parent / "test_images" / "test_image.jpg"

pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
async def test_health_check():
    """Test the health check endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{AI_SERVICE_URL}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_background_removal():
    """Test the background removal endpoint"""
    if not TEST_IMAGE_PATH.exists():
        pytest.skip("Test image not found")

    async with httpx.AsyncClient() as client:
        with open(TEST_IMAGE_PATH, "rb") as f:
            files = {"file": ("test_image.jpg", f, "image/jpeg")}
            response = await client.post(
                f"{AI_SERVICE_URL}/remove-background",
                files=files
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"
            
            # Verify the response is a valid image
            img = Image.open(io.BytesIO(response.content))
            assert img.mode == "RGBA"  # Background removed images should have alpha channel

@pytest.mark.asyncio
async def test_enhance():
    """Test the image enhancement endpoint"""
    if not TEST_IMAGE_PATH.exists():
        pytest.skip("Test image not found")

    async with httpx.AsyncClient() as client:
        with open(TEST_IMAGE_PATH, "rb") as f:
            files = {"file": ("test_image.jpg", f, "image/jpeg")}
            response = await client.post(
                f"{AI_SERVICE_URL}/enhance",
                files=files,
                data={"scale_factor": 2.0}
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"
            
            # Verify the response is a valid image
            img = Image.open(io.BytesIO(response.content))
            assert img.size[0] > 0 and img.size[1] > 0

@pytest.mark.asyncio
async def test_smart_crop():
    """Test the smart crop endpoint"""
    if not TEST_IMAGE_PATH.exists():
        pytest.skip("Test image not found")

    async with httpx.AsyncClient() as client:
        with open(TEST_IMAGE_PATH, "rb") as f:
            files = {"file": ("test_image.jpg", f, "image/jpeg")}
            response = await client.post(
                f"{AI_SERVICE_URL}/smart-crop",
                files=files,
                data={"width": 300, "height": 300}
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"
            
            # Verify the response is a valid image with correct dimensions
            img = Image.open(io.BytesIO(response.content))
            assert img.size == (300, 300)

def test_all():
    """Run all tests"""
    asyncio.run(test_health_check())
    asyncio.run(test_background_removal())
    asyncio.run(test_enhance())
    asyncio.run(test_smart_crop())

if __name__ == "__main__":
    test_all() 