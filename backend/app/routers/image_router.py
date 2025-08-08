from fastapi import APIRouter, Request, HTTPException, Cookie
from app.services.supabase_service import supabase
import uuid
import logging
import jwt
import os

image_router = APIRouter()
logger = logging.getLogger("image_router")

JWT_SECRET = os.getenv("JWT_SECRET")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

def validate_uuid(id_str: str) -> str | None:
    try:
        return str(uuid.UUID(id_str))
    except Exception:
        return None

@image_router.get("/status/{image_id}")
async def get_image_status(image_id: str):
    """
    Fetch the status of an image by its UUID.
    """
    valid_id = validate_uuid(image_id)
    if not valid_id:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    try:
        result = (
            supabase
            .table("images")
            .select("*")
            .eq("id", valid_id)
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Image not found")

        return {
            "success": True,
            "id": result.data["id"],
            "status": result.data["status"],
            "original_path": result.data.get("original_path"),
            "processed_path": result.data.get("processed_path"),
            "error": result.data.get("error_message")
        }

    except Exception as e:
        logger.error(f"Error fetching image status: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch image status")

@image_router.get("/images")
async def get_images_by_shop(session: str = Cookie(None)):
    """
    Fetch all images belonging to the authenticated shop.
    """
    if not session:
        raise HTTPException(status_code=401, detail="Missing session")

    try:
        payload = jwt.decode(session, JWT_SECRET, algorithms=["HS256"])
        shop = payload.get("shop")
        if not shop:
            raise Exception("Shop not found in session")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except Exception as e:
        logger.warning(f"Session decode failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        result = (
            supabase
            .table("images")
            .select("*")
            .eq("shop", shop)
            .order("created_at", desc=True)
            .execute()
        )
        return {"images": result.data}
    except Exception as e:
        logger.error(f"Failed to fetch images for shop {shop}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching images")
