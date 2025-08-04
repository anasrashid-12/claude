from fastapi import APIRouter, HTTPException, Request, Depends
from app.services.supabase_service import supabase
from app.dependencies.auth import get_current_shop
from app.logging_config import logger

router = APIRouter()

SETTINGS_TABLE = "settings"

# ✅ Get current shop settings
@router.get("/settings")
async def get_settings(shop: str = Depends(get_current_shop)):
    try:
        response = supabase.table(SETTINGS_TABLE).select("*").eq("shop", shop).limit(1).execute()
        if response.data:
            return response.data[0]
        return {}
    except Exception as e:
        logger.error(f"GET /settings failed: {e}")
        raise HTTPException(status_code=500, detail="Error fetching settings")

# ✅ Insert or update settings (Upsert)
@router.post("/settings")
async def upsert_settings(request: Request, shop: str = Depends(get_current_shop)):
    try:
        body = await request.json()
        new_data = {
            "shop": shop,
            "background_removal": body.get("background_removal", False),
            "optimize_images": body.get("optimize_images", False),
            "avatar_url": body.get("avatar_url", "")
        }

        response = supabase.table(SETTINGS_TABLE).upsert(new_data, on_conflict=["shop"]).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        logger.error(f"POST /settings failed: {e}")
        raise HTTPException(status_code=500, detail="Error saving settings")

# ✅ Update settings by shop (specific fields)
@router.put("/settings")
async def update_settings(request: Request, shop: str = Depends(get_current_shop)):
    try:
        body = await request.json()
        update_data = {
            k: v for k, v in body.items()
            if k in ["background_removal", "optimize_images", "avatar_url"]
        }
        response = supabase.table(SETTINGS_TABLE).update(update_data).eq("shop", shop).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        logger.error(f"PUT /settings failed: {e}")
        raise HTTPException(status_code=500, detail="Error updating settings")

# ✅ Delete settings for current shop
@router.delete("/settings")
async def delete_settings(shop: str = Depends(get_current_shop)):
    try:
        supabase.table(SETTINGS_TABLE).delete().eq("shop", shop).execute()
        return {"deleted": True}
    except Exception as e:
        logger.error(f"DELETE /settings failed: {e}")
        raise HTTPException(status_code=500, detail="Error deleting settings")
