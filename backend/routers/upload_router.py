from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Cookie
from fastapi.responses import JSONResponse
from services.supabase import supabase
from logging_config import logger
import uuid
import os
import jwt

upload_router = APIRouter()

BUCKET_NAME = "makeit3d-public"
SUPABASE_URL = os.getenv("SUPABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET", "maxflow_secret")

if not SUPABASE_URL:
    raise RuntimeError("Missing SUPABASE_URL in environment")

@upload_router.post("/upload")
async def upload_image(request: Request, image: UploadFile = File(...), session: str = Cookie(None)):
    try:
        # 🧠 Decode shop from JWT session
        if not session:
            raise HTTPException(status_code=401, detail="Missing session token")

        payload = jwt.decode(session, JWT_SECRET, algorithms=["HS256"])
        shop = payload.get("shop")
        if not shop:
            raise HTTPException(status_code=401, detail="Invalid session: missing shop")

        # 🖼️ Generate unique filename and read content
        ext = os.path.splitext(image.filename)[-1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        content = await image.read()

        # ☁️ Upload to Supabase Storage
        response = supabase.storage.from_(BUCKET_NAME).upload(
            unique_filename,
            content,
            {"content-type": image.content_type}
        )

        if hasattr(response, "error") and response.error:
            logger.error(f"[Upload] Supabase error: {response.error.message}")
            raise HTTPException(status_code=500, detail="Failed to upload to Supabase")

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{unique_filename}"
        logger.info(f"[Upload] Image uploaded: {public_url}")

        # 📝 Insert into Supabase `images` table
        image_id = str(uuid.uuid4())
        try:
            supabase.table("images").insert({
                "id": image_id,
                "shop": shop,
                "image_url": public_url,
                "status": "queued"
            }).execute()
        except Exception as e:
            logger.error(f"[Upload] DB insert failed: {e}")
            raise HTTPException(status_code=500, detail="Upload succeeded but DB insert failed")

        return {
            "message": "Uploaded and logged",
            "filename": unique_filename,
            "url": public_url,
            "image_id": image_id
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid session token")
    except Exception as e:
        logger.error(f"[Upload] Failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")
