from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Cookie
import uuid, os, jwt, requests
from app.logging_config import logger
from app.services.supabase_service import supabase  # your own Supabase
from app.services.supabase_custom import upload_to_makeit3d_bucket  # MakeIt3D bucket

upload_router = APIRouter()

YOUR_BUCKET = "makeit3d-public"  # your own bucket
MAKEIT3D_BUCKET = "makeit3d-public"
YOUR_SUPABASE_URL = os.getenv("SUPABASE_URL")
MAKEIT3D_SUPABASE_URL = "https://ftnkfcuhjmmedmoekvwg.supabase.co"
JWT_SECRET = os.getenv("JWT_SECRET")
MAKEIT3D_API_KEY = os.getenv("MAKEIT3D_API_KEY")

@upload_router.post("/upload")
async def upload_image(request: Request, image: UploadFile = File(...), session: str = Cookie(None)):
    if not session:
        raise HTTPException(status_code=401, detail="Missing session")

    try:
        payload = jwt.decode(session, JWT_SECRET, algorithms=["HS256"])
        shop = payload.get("shop")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session token")

    if not shop:
        raise HTTPException(status_code=401, detail="Invalid session")

    ext = os.path.splitext(image.filename)[-1]
    filename = f"{uuid.uuid4().hex}{ext}"
    content = await image.read()

    # 1. Upload to your own Supabase (for gallery)
    logger.info(f"📥 Uploading to your Supabase bucket '{YOUR_BUCKET}'...")
    response = supabase.storage.from_(YOUR_BUCKET).upload(
        filename, content, {"content-type": image.content_type}
    )
    if hasattr(response, "error") and response.error:
        logger.error("🔥 Upload to your Supabase failed")
        raise HTTPException(status_code=500, detail="Your Supabase upload failed")

    your_image_url = f"{YOUR_SUPABASE_URL}/storage/v1/object/public/{YOUR_BUCKET}/{filename}"

    # 2. Upload to MakeIt3D Supabase (required for processing)
    logger.info(f"📤 Uploading to MakeIt3D bucket '{MAKEIT3D_BUCKET}'...")
    makeit3d_uploaded = upload_to_makeit3d_bucket(filename, content, image.content_type)

    if not makeit3d_uploaded:
        raise HTTPException(status_code=500, detail="Upload to MakeIt3D Supabase failed")

    makeit3d_url = f"{MAKEIT3D_SUPABASE_URL}/storage/v1/object/public/{MAKEIT3D_BUCKET}/{filename}"

    # 3. Submit MakeIt3D processing task
    task_id = f"{shop}-remove-bg-{uuid.uuid4().hex}"
    payload = {
        "task_id": task_id,
        "provider": "stability",
        "input_image_asset_url": makeit3d_url,
        "output_format": "png"
    }

    logger.info(f"🛠️ Submitting to MakeIt3D: {payload}")
    try:
        res = requests.post(
            "https://api.makeit3d.io/generate/remove-background",
            headers={"X-API-Key": MAKEIT3D_API_KEY, "Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        res.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"🔥 MakeIt3D job submission failed: {res.status_code} - {res.text}")
        raise HTTPException(status_code=500, detail="MakeIt3D processing failed")

    # 4. Save to your DB
    image_id = str(uuid.uuid4())
    supabase.table("images").insert({
        "id": image_id,
        "shop": shop,
        "image_url": your_image_url,
        "makeit3d_task_id": task_id,
        "status": "queued"
    }).execute()

    return {
        "message": "Upload and processing started",
        "image_id": image_id,
        "task_id": task_id,
        "image_url": your_image_url
    }
