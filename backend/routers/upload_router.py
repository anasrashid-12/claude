from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import uuid
from logging_config import logger

upload_router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

@upload_router.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    try:
        # Ensure safe unique filename
        ext = os.path.splitext(image.filename)[-1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Save file
        with open(file_path, "wb") as f:
            f.write(await image.read())

        logger.info(f"[Upload] Image saved: {unique_filename}")

        return {
            "message": "Uploaded",
            "filename": unique_filename,
            "url": f"{BACKEND_URL}/uploads/{unique_filename}"
        }
    except Exception as e:
        logger.error(f"[Upload] Failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image")


@upload_router.get("/uploads/{filename}")
async def serve_uploaded_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        logger.warning(f"[Upload] File not found: {filename}")
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, media_type="image/png", filename=filename)

__all__ = ["upload_router"]
