from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Form
from app.services.supabase_service import supabase
from app.logging_config import logger
from app.tasks.image_tasks import submit_job_task
import uuid
import os
import jwt
from datetime import timedelta

upload_router = APIRouter()

YOUR_BUCKET = "makeit3d-private"
JWT_SECRET = os.getenv("JWT_SECRET")

@upload_router.post("/upload")
async def upload_image(request: Request, file: UploadFile = File(...), operation: str = Form(...)):
    try:
        token = request.cookies.get("session")
        if not token:
            raise HTTPException(status_code=401, detail="Unauthorized")

        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        shop = payload.get("shop")
        if not shop:
            raise HTTPException(status_code=401, detail="Invalid token")

        filename = f"{uuid.uuid4()}.png"
        path = f"{shop}/{filename}"  # Per-shop folder
        file_content = await file.read()

        # Upload to private bucket
        upload_res = supabase.storage.from_(YOUR_BUCKET).upload(path, file_content, {
            "content-type": "image/png",
            "x-upsert": "true"
        })
        if not upload_res or getattr(upload_res, "status_code", 500) >= 400:
            logger.error(f"[Upload] Failed upload: {upload_res}")
            raise HTTPException(status_code=500, detail="Supabase upload failed")

        # Create signed URL (valid for 6 hours)
        signed_url_res = supabase.storage.from_(YOUR_BUCKET).create_signed_url(path, expires_in=6 * 3600)
        signed_url = signed_url_res.get("signedURL")
        if not signed_url:
            logger.error(f"[Signed URL] Failed to generate signed URL: {signed_url_res}")
            raise HTTPException(status_code=500, detail="Signed URL generation failed")

        image_data = {
            "shop": shop,
            "status": "queued",
            "filename": path,
            "original_url": signed_url,
            "operation": operation,
        }

        result = supabase.table("images").insert(image_data).execute()
        image_id = result.data[0]["id"]

        submit_job_task.delay(image_id, operation, signed_url)

        return {"message": "Image uploaded and processing started", "id": image_id}

    except Exception as e:
        logger.error(f"Upload failed: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail="Upload failed")
