import os
from supabase import create_client
import logging

logger = logging.getLogger("supabase_service")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("❌ Missing Supabase credentials in environment")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def save_shop_token(shop: str, access_token: str):
    """
    Upserts the shop and its access token into the 'shops' table.
    """
    try:
        response = supabase.table("shops").upsert({
            "shop": shop,
            "access_token": access_token
        }).execute()
        logger.info(f"[Supabase] ✅ Token saved for shop: {shop}")
        return response
    except Exception as e:
        logger.error(f"[Supabase] ❌ Failed to save token: {e}")
        raise


def upload_to_storage(bucket: str, path: str, file_bytes: bytes, content_type: str = "image/png"):
    """
    Uploads a file to Supabase Storage and returns the public URL.
    """
    try:
        response = supabase.storage.from_(bucket).upload(
            path=path,
            file=file_bytes,
            file_options={"content-type": content_type},
            upsert=True
        )

        if response.get("error"):
            raise Exception(response["error"]["message"])

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}"
        logger.info(f"[Supabase] ✅ File uploaded to: {public_url}")
        return public_url

    except Exception as e:
        logger.error(f"[Supabase] ❌ Storage upload failed: {e}")
        raise
