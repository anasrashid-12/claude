from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Form
from app.services.supabase_service import supabase
from app.logging_config import logger
from app.tasks.image_tasks import submit_job_task
import uuid
import os
import jwt

upload_router = APIRouter()

YOUR_BUCKET = "makeit3d-public"
SUPABASE_URL = os.getenv("SUPABASE_URL")

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
        file_content = await file.read()

        res = supabase.storage.from_(YOUR_BUCKET).upload(f"{shop}/{filename}", file_content, {"content-type": "image/png"})
        if res.get("error"):
            raise HTTPException(status_code=500, detail=res["error"]["message"])

        public_url_res = supabase.storage.from_(YOUR_BUCKET).get_public_url(f"{shop}/{filename}")
        image_url = public_url_res.get("publicUrl")

        if not image_url:
            raise HTTPException(status_code=500, detail="Failed to get public URL")

        image_data = {
            "shop": shop,
            "status": "queued",
            "original_url": image_url,
            "operation": operation,
        }

        result = supabase.table("images").insert(image_data).execute()
        image_id = result.data[0]["id"]

        submit_job_task.delay(image_id, operation, image_url)

        return {"message": "Image uploaded and processing started", "id": image_id}

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")
