from fastapi import APIRouter, Request, HTTPException, Cookie
from app.tasks.image_tasks import submit_job_task
from app.services.supabase_service import supabase
import uuid
import logging
import jwt
import os

image_router = APIRouter()
logger = logging.getLogger("image_router")

JWT_SECRET = os.getenv("JWT_SECRET", "maxflow_secret")
SUPABASE_URL = os.getenv("SUPABASE_URL")
BUCKET_NAME = "makeit3d-public"

def validate_uuid(id_str: str):
    try:
        return str(uuid.UUID(id_str))
    except Exception:
        return None

@image_router.post("/process")
async def process_image(request: Request, session: str = Cookie(None)):
    if not session:
        raise HTTPException(status_code=401, detail="Missing session")

    try:
        payload = jwt.decode(session, JWT_SECRET, algorithms=["HS256"])
        shop = payload.get("shop")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session")

    data = await request.json()
    filename = data.get("filename")
    operation = data.get("operation")

    if not filename or not operation:
        raise HTTPException(status_code=400, detail="Missing filename or operation")

    image_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{filename}"

    result = supabase.table("images").select("id").eq("shop", shop).eq("filename", filename).single().execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Image not found. Make sure it is uploaded first.")

    image_id = result.data["id"]

    # ✅ Now call the new task
    task = submit_job_task.delay(image_id, operation, image_url)

    return {
        "success": True,
        "message": "Image queued for processing",
        "task_id": task.id,
        "image_id": image_id,
        "image_url": image_url
    }

@image_router.get("/status/{image_id}")
async def get_image_status(image_id: str):
    valid_id = validate_uuid(image_id)
    if not valid_id:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    result = supabase.table("images").select("*").eq("id", valid_id).single().execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Image not found")

    return {
        "success": True,
        "id": result.data["id"],
        "status": result.data["status"],
        "original_url": result.data.get("image_url"),
        "processed_url": result.data.get("processed_url"),
        "error": result.data.get("error_message")
    }

@image_router.get("/images")
async def get_images_by_shop(session: str = Cookie(None)):
    if not session:
        raise HTTPException(status_code=401, detail="Missing session")

    try:
        payload = jwt.decode(session, JWT_SECRET, algorithms=["HS256"])
        shop = payload.get("shop")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session")

    result = supabase.table("images").select("*").eq("shop", shop).order("created_at", desc=True).execute()

    return {"images": result.data}
