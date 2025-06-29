from fastapi import APIRouter, Request, HTTPException, Cookie
from app.tasks.image_tasks import process_image_task
from app.services.supabase_service import supabase
import uuid
import logging
import jwt
import os

image_router = APIRouter()
logger = logging.getLogger("image_router")

JWT_SECRET = os.getenv("JWT_SECRET", "maxflow_secret")


def validate_uuid(id_str: str):
    try:
        return str(uuid.UUID(id_str))
    except Exception:
        return None


# ✅ Queue an image for processing
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
    image_url = data.get("image_url")
    if not image_url:
        raise HTTPException(status_code=400, detail="Missing image_url")

    image_id = str(uuid.uuid4())

    # Save to Supabase
    supabase.table("images").insert({
        "id": image_id,
        "shop": shop,
        "image_url": image_url,
        "status": "queued"
    }).execute()

    # Send to Celery task
    task = process_image_task.delay(image_id, image_url)

    return {
        "success": True,
        "message": "Image queued",
        "task_id": task.id,
        "image_id": image_id,
    }


# ✅ Get status of a specific image
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


# ✅ Get all images for the current shop (via session)
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
