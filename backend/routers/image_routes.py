from fastapi import APIRouter, HTTPException, Request
from tasks.image_tasks import process_image_task
from services.supabase import supabase
import uuid
import logging

image_router = APIRouter()
logger = logging.getLogger(__name__)

@image_router.post("/process")
async def process_image(request: Request):
    try:
        data = await request.json()
        image_url = data.get("image_url")
        shop = data.get("shop")

        if not image_url or not shop:
            raise HTTPException(status_code=400, detail="Missing image_url or shop")

        image_id = str(uuid.uuid4())

        result = supabase.table("images").insert({
            "id": image_id,
            "shop": shop,
            "image_url": image_url,
            "status": "queued"
        }).execute()

        if result.error:
            raise HTTPException(status_code=500, detail="Supabase insert failed")

        # Send to Celery (which will use MakeIt3D API now)
        task = process_image_task.delay(image_id, image_url)

        return {
            "success": True,
            "message": "Image queued for processing",
            "task_id": task.id,
            "image_id": image_id
        }

    except Exception as e:
        logger.error(f"Image queue error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@image_router.get("/{image_id}")
async def get_image_status(image_id: str):
    try:
        result = supabase.table("images").select("*").eq("id", image_id).single().execute()

        if result.data:
            return {
                "success": True,
                "id": result.data["id"],
                "status": result.data["status"],
                "original_url": result.data.get("image_url"),
                "processed_url": result.data.get("processed_url"),
                "error": result.data.get("error_message")
            }

        raise HTTPException(status_code=404, detail="Image not found")

    except Exception as e:
        logger.error(f"Fetch status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@image_router.get("/supabase/get-images")
async def get_images_by_shop(shop: str):
    try:
        result = supabase.table("images").select("*").eq("shop", shop).order("created_at", desc=True).execute()
        return {"images": result.data}
    except Exception as e:
        logger.error(f"Error fetching images by shop: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
__all__ = ["image_router"]