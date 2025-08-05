from fastapi import APIRouter, HTTPException, Request, Depends, UploadFile, File
from app.services.supabase_service import supabase
from app.dependencies.auth import get_current_shop
from app.logging_config import logger

settings_router = APIRouter()
SETTINGS_TABLE = "settings"
AVATAR_BUCKET = "avatars"

@settings_router.get("/settings")
async def get_settings(shop: str = Depends(get_current_shop)):
    try:
        response = supabase.table(SETTINGS_TABLE).select("*").eq("shop", shop).limit(1).execute()
        data = response.data[0] if response.data else {}

        # If avatar_path exists, generate signed URL
        avatar_path = data.get("avatar_path")
        if avatar_path:
            signed = supabase.storage.from_(AVATAR_BUCKET).create_signed_url(avatar_path, 3600 * 24 * 7)
            if not signed.error:
                data["avatar_path"] = signed.data.get("signedURL")

        return data
    except Exception as e:
        logger.error(f"GET /settings failed: {e}")
        raise HTTPException(status_code=500, detail="Error fetching settings")

@settings_router.post("/settings")
async def upsert_settings(request: Request, shop: str = Depends(get_current_shop)):
    try:
        body = await request.json()
        new_data = {
            "shop": shop,
            "background_removal": body.get("background_removal", False),
            "optimize_images": body.get("optimize_images", False),
        }
        response = supabase.table(SETTINGS_TABLE).upsert(new_data, on_conflict=["shop"]).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        logger.error(f"POST /settings failed: {e}")
        raise HTTPException(status_code=500, detail="Error saving settings")

@settings_router.post("/settings/avatar")
async def upload_avatar(file: UploadFile = File(...), shop: str = Depends(get_current_shop)):
    try:
        contents = await file.read()
        ext = file.filename.split('.')[-1]
        avatar_path = f"{shop}/avatar.{ext}"

        # Upload file to Supabase storage
        upload_res = supabase.storage.from_(AVATAR_BUCKET).upload(
            avatar_path,
            contents,
            {
                "content-type": file.content_type,
                "x-upsert": "true"
            }
        )

        if upload_res.error:
            raise HTTPException(status_code=500, detail=f"Upload error: {upload_res.error.message}")

        # Update settings table with avatar path
        update_res = supabase.table(SETTINGS_TABLE).update({
            "avatar_path": avatar_path
        }).eq("shop", shop).execute()

        if update_res.error:
            raise HTTPException(status_code=500, detail=f"DB update error: {update_res.error.message}")

        # Generate signed URL
        signed_url_res = supabase.storage.from_(AVATAR_BUCKET).create_signed_url(
            avatar_path, 3600 * 24 * 7
        )

        if signed_url_res.error:
            raise HTTPException(status_code=500, detail=f"Signed URL error: {signed_url_res.error.message}")

        return {"url": signed_url_res.data.get("signedURL")}

    except Exception as e:
        logger.error(f"POST /settings/avatar failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@settings_router.get("/settings/avatar/refresh")
async def refresh_avatar_url(shop: str = Depends(get_current_shop)):
    try:
        res = supabase.table(SETTINGS_TABLE).select("avatar_path").eq("shop", shop).limit(1).execute()

        if not res.data or not isinstance(res.data, list) or not res.data[0].get("avatar_path"):
            raise HTTPException(status_code=404, detail="Avatar not found")

        avatar_path = res.data[0]["avatar_path"]
        signed = supabase.storage.from_(AVATAR_BUCKET).create_signed_url(avatar_path, 3600 * 24 * 7)

        if signed.error:
            raise HTTPException(status_code=500, detail=f"Signed URL error: {signed.error.message}")

        return {"url": signed.data.get("signedURL")}

    except Exception as e:
        logger.error(f"GET /settings/avatar/refresh failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
