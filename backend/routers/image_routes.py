from fastapi import APIRouter, HTTPException, Request
from tasks.image_tasks import process_image_task
from services.supabase import supabase
import uuid
import logging

image_router = APIRouter()
logger = logging.getLogger("image_router")

@image_router.post("/process")
async def process_image(request: Request):
    try:
        data = await request.json()
        image_url = data.get("image_url")
        shop = data.get("shop")

        if not image_url or not shop:
            raise HTTPException(status_code=400, detail="Missing image_url or shop")

        image_id = str(uuid.uuid4())

        # Insert image metadata into Supabase with initial status
        result = supabase.table("images").insert({
            "id": image_id,
            "shop": shop,
            "image_url": image_url,
            "status": "queued"
        }).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to insert image record")

        logger.info(f"[Queue] Image {image_id} queued by {shop}")

        # Trigger async Celery task
        task = process_image_task.delay(image_id, image_url)

        return {
            "success": True,
            "message": "✅ Image queued for processing",
            "task_id": task.id,
            "image_id": image_id
        }

    except Exception as e:
        logger.error(f"[Queue] Error queuing image: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@image_router.get("/{image_id}")
async def get_image_status(image_id: str):
    try:
        result = supabase.table("images").select("*").eq("id", image_id).single().execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Image not found")

        logger.info(f"[Status] Fetched status for image {image_id}")
        return {
            "success": True,
            "id": result.data["id"],
            "status": result.data["status"],
            "original_url": result.data.get("image_url"),
            "processed_url": result.data.get("processed_url"),
            "error": result.data.get("error_message")
        }

    except Exception as e:
        logger.error(f"[Status] Error retrieving image status: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch image status")


@image_router.get("/supabase/get-images")
async def get_images_by_shop(shop: str):
    try:
        result = supabase.table("images").select("*").eq("shop", shop).order("created_at", desc=True).execute()
        logger.info(f"[Images] Retrieved images for shop {shop} - Count: {len(result.data)}")
        return {"images": result.data}
    except Exception as e:
        logger.error(f"[Images] Error fetching shop images: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch images")

__all__ = ["image_router"]
