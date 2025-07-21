from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Cookie, Form
import uuid, os, jwt
from app.logging_config import logger
from app.services.supabase_service import supabase

upload_router = APIRouter()

YOUR_BUCKET = "makeit3d-public"
YOUR_SUPABASE_URL = os.getenv("SUPABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET")

MAX_FILE_SIZE_MB = 5

@upload_router.post("/upload")
async def upload_image(
    request: Request,
    image: UploadFile = File(...),
    operation: str = Form(...),
    session: str = Cookie(None)
):
    if not session:
        raise HTTPException(status_code=401, detail="Missing session")

    try:
        payload = jwt.decode(session, JWT_SECRET, algorithms=["HS256"])
        shop = payload.get("shop")
    except Exception as e:
        logger.error(f"❌ Invalid JWT session: {e}")
        raise HTTPException(status_code=401, detail="Invalid session token")

    if not shop:
        raise HTTPException(status_code=401, detail="Invalid session: shop missing")

    logger.info(f"✅ Uploading image for shop: {shop} with operation: {operation}")

    # ✅ Validate file size (max 5MB)
    content = await image.read()
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File size exceeds {MAX_FILE_SIZE_MB}MB limit")

    ext = os.path.splitext(image.filename)[-1]
    filename = f"uploads/{uuid.uuid4().hex}{ext}"

    logger.info(f"📥 Uploading file '{filename}' ({round(file_size_mb, 2)}MB) to bucket '{YOUR_BUCKET}'...")
    response = supabase.storage.from_(YOUR_BUCKET).upload(
        filename, content, {"content-type": image.content_type}
    )

    logger.info(f"📝 Upload Response: {response}")
    if hasattr(response, "error") and response.error:
        logger.error(f"🔥 Upload failed: {response.error}")
        raise HTTPException(status_code=500, detail="Your Supabase upload failed")

    your_image_url = f"{YOUR_SUPABASE_URL}/storage/v1/object/public/{YOUR_BUCKET}/{filename}"
    logger.info(f"✅ Uploaded URL: {your_image_url}")

    image_id = str(uuid.uuid4())
    insert_res = supabase.table("images").insert({
        "id": image_id,
        "shop": shop,
        "filename": filename,
        "image_url": your_image_url,
        "status": "queued",
        "operation": operation
    }).execute()

    logger.info(f"📝 Insert Response: {insert_res}")
    if hasattr(insert_res, "error") and insert_res.error:
        logger.error(f"🔥 Insert failed: {insert_res.error}")
        raise HTTPException(status_code=500, detail="Failed to insert image record")

    return {
        "message": "✅ Image uploaded and queued",
        "image_id": image_id,
        "image_url": your_image_url,
        "filename": filename
    }
