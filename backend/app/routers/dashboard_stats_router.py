from fastapi import APIRouter, Request, HTTPException, Cookie
from app.services.supabase_service import supabase
from app.services.signed_url_util import get_signed_url
import jwt
import os
import logging

dashboard_stats_router = APIRouter()
logger = logging.getLogger("dashboard_stats")

JWT_SECRET = os.getenv("JWT_SECRET", "maxflow_secret")

@dashboard_stats_router.post("/image/dashboard-stats")
async def get_dashboard_stats(request: Request, session: str = Cookie(None)):
    if not session:
        raise HTTPException(status_code=401, detail="Missing session")

    try:
        payload = jwt.decode(session, JWT_SECRET, algorithms=["HS256"])
        shop = payload.get("shop")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        # Get all images for stats
        images_res = (
            supabase.table("images")
            .select("*")
            .eq("shop", shop)
            .order("created_at", desc=True)
            .execute()
        )
        images = images_res.data or []

        total = len(images)
        processing = sum(1 for img in images if img["status"] == "processing")
        failed = sum(1 for img in images if img["status"] in ["error", "failed"])
        completed = sum(1 for img in images if img["status"] == "processed")

        # Fetch recent processed images only
        recent_res = (
            supabase.table("images")
            .select("*")
            .eq("shop", shop)
            .eq("status", "processed")
            .order("created_at", desc=True)
            .limit(5)
            .execute()
        )
        recent_images = recent_res.data or []

        recent = []
        for img in recent_images:
            try:
                processed_path = img.get("processed_path")
                if not processed_path:
                    continue

                signed_url = get_signed_url(processed_path)

                recent.append({
                    "url": signed_url,
                    "product": "Imported Image",
                    "status": format_status(img["status"])
                })
            except Exception as e:
                logger.warning(f"Could not create signed URL for image {img.get('id')}: {e}")

        return {
            "stats": {
                "total": total,
                "processing": processing,
                "failed": failed,
                "completed": completed
            },
            "recent": recent
        }

    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard stats")

def format_status(status: str) -> str:
    if status in ["processed"]:
        return "Complete"
    elif status in ["queued", "processing"]:
        return "Importing"
    elif status in ["error", "failed"]:
        return "Failed"
    return status.capitalize()
