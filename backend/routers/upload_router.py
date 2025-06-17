# backend/routers/upload_router.py
from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from logging_config import logger

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, image.filename)
    with open(file_path, "wb") as f:
        f.write(await image.read())
    logger.info(f"Image uploaded: {image.filename}")
    return {"message": "Uploaded", "filename": image.filename}
