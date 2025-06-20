from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
from logging_config import logger

upload_router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

@upload_router.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, image.filename)
        with open(file_path, "wb") as f:
            f.write(await image.read())

        logger.info(f"Image uploaded: {image.filename}")

        return {
            "message": "Uploaded",
            "filename": image.filename,
            "url": f"{BACKEND_URL}/uploads/{image.filename}"
        }
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image")


@upload_router.get("/uploads/{filename}")
async def serve_uploaded_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, media_type="image/png", filename=filename)

__all__ = ["upload_router"]