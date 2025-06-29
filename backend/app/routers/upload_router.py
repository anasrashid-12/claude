from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Cookie
from app.services.supabase_service import supabase
import uuid
import os
import jwt
import requests
from app.logging_config import logger

upload_router = APIRouter()

BUCKET_NAME = "makeit3d-public"
SUPABASE_URL = os.getenv("SUPABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
MAKEIT3D_API_KEY = os.getenv("MAKEIT3D_API_KEY")


@upload_router.post("/upload")
async def upload_image(
    request: Request, 
    image: UploadFile = File(...), 
    session: str = Cookie(None)
):
    if not session:
        raise HTTPException(status_code=401, detail="Missing session token")

    payload = jwt.decode(session, JWT_SECRET, algorithms=["HS256"])
    shop = payload.get("shop")

    if not shop:
        raise HTTPException(status_code=401, detail="Invalid session")

    ext = os.path.splitext(image.filename)[-1]
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    content = await image.read()

    # Upload to Supabase Storage
    supabase.storage.from_(BUCKET_NAME).upload(
        unique_filename, content, {"content-type": image.content_type}
    )

    your_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{unique_filename}"

    # Upload to MakeIt3D Storage
    makeit3d_upload = requests.post(
        "https://api.makeit3d.io/auth/upload",
        headers={"X-API-Key": MAKEIT3D_API_KEY, "Content-Type": "application/json"},
        json={"source_url": your_url, "filename": unique_filename},
        timeout=30,
    )

    if makeit3d_upload.status_code != 200:
        raise HTTPException(status_code=500, detail="Upload to MakeIt3D failed")

    makeit3d_url = makeit3d_upload.json().get("uploaded_url")

    image_id = str(uuid.uuid4())
    logger.info(f"Inserting image with ID: {image_id}")

    supabase.table("images").insert({
        "id": image_id,
        "shop": shop,
        "image_url": your_url,
        "makeit3d_url": makeit3d_url,
        "status": "queued"
    }).execute()

    return {
        "message": "Uploaded successfully",
        "url": your_url,
        "makeit3d_url": makeit3d_url,
        "image_id": image_id
    }
