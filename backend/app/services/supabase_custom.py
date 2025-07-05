import os
import requests
from app.logging_config import logger

# Constants
MAKEIT3D_SUPABASE_URL = "https://ftnkfcuhjmmedmoekvwg.supabase.co"
MAKEIT3D_BUCKET = "makeit3d-public"
MAKEIT3D_SUPABASE_API_KEY = os.getenv("MAKEIT3D_SUPABASE_SERVICE_KEY")  # Required

def upload_to_makeit3d_bucket(filename: str, content: bytes, content_type: str) -> bool:
    """Uploads an image to the MakeIt3D Supabase bucket via HTTP"""
    url = f"{MAKEIT3D_SUPABASE_URL}/storage/v1/object/{MAKEIT3D_BUCKET}/{filename}"

    headers = {
        "Authorization": f"Bearer {MAKEIT3D_SUPABASE_API_KEY}",
        "Content-Type": content_type,
        "x-upsert": "true",  # Overwrite if exists
    }

    logger.info(f"📡 Uploading to MakeIt3D Supabase at {url}...")
    try:
        response = requests.post(url, headers=headers, data=content, timeout=15)
        if response.status_code == 200:
            logger.info("✅ Upload to MakeIt3D Supabase successful")
            return True
        else:
            logger.error(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False
    except requests.RequestException as e:
        logger.error(f"🔥 Upload to MakeIt3D Supabase failed: {e}")
        return False
