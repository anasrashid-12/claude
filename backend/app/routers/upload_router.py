from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Cookie, Form
from starlette.responses import JSONResponse
import uuid
import os
import jwt
import traceback

from app.logging_config import logger
from app.services.supabase_service import supabase
from app.tasks.image_tasks import submit_job_task

upload_router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "makeit3d-public")
JWT_SECRET = os.getenv("JWT_SECRET")


@upload_router.post("/upload")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    operation: str = Form(...),
    session: str = Cookie(None),
):
    if not session:
        raise HTTPException(status_code=401, detail="No session token found")

    try:
        payload = jwt.decode(session, JWT_SECRET, algorithms=["HS256"])
        shop = payload.get("shop")
        shop_id = payload.get("shop_id")
    except Exception as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(status_code=401, detail="Invalid session token")

    filename = f"{uuid.uuid4()}.png"
    path = f"{shop}/upload/{filename}"

    try:
        # Read file content into bytes
        file_content = await file.read()
        logger.info(f"Uploading file for shop {shop}: {filename} → {path}")

        # ✅ FIX: Upload using raw bytes, not BytesIO
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=path,
            file=file_content,  # 👈 pass raw bytes here
            file_options={"content-type": file.content_type},
        )

        # Generate signed URL
        signed_url_res = supabase.storage.from_(SUPABASE_BUCKET).create_signed_url(
            path=path, expires_in=60 * 60 * 24 * 7
        )
        signed_url = signed_url_res.get("signedURL")
        if not signed_url:
            raise Exception("Signed URL generation failed")

        # Insert image record in DB
        insert_response = supabase.table("images").insert({
            "shop": shop_id,
            "original_url": signed_url,
            "status": "pending",
            "operation": operation,
            "filename": file.filename
        }).execute()

        if not insert_response.data:
            raise Exception("Image insert failed in Supabase")

        image_id = insert_response.data[0]["id"]

        # Queue job to Celery
        submit_job_task.delay(
            image_id=image_id,
            operation=operation,
            image_url=signed_url,
            shop=shop
        )

        return JSONResponse(content={"id": image_id, "status": "queued"}, status_code=202)

    except Exception as e:
        logger.error(f"Upload failed: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Upload failed")
