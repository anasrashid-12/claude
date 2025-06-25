import os
import logging
from supabase import create_client

logger = logging.getLogger("supabase_service")

# 🔑 Environment Variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# 🛑 Check for required credentials
if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("❌ Missing Supabase credentials in environment")

# 🔗 Supabase Client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


# 🚀 Save or update shop token in 'shops' table
def save_shop_token(shop: str, access_token: str):
    try:
        response = supabase.table("shops").upsert({
            "shop": shop,
            "access_token": access_token,
        }).execute()

        logger.info(f"[Supabase] ✅ Token saved for shop: {shop}")
        return response

    except Exception as e:
        logger.error(f"[Supabase] ❌ Failed to save token for {shop}: {e}")
        raise


# ☁️ Upload file to Supabase Storage (public URL)
def upload_to_storage(bucket: str, path: str, file_bytes: bytes, content_type: str = "image/png"):
    try:
        result = supabase.storage.from_(bucket).upload(
            path=path,
            file=file_bytes,
            file_options={"content-type": content_type},
            upsert=True
        )

        if hasattr(result, "error") and result.error:
            logger.error(f"[Supabase] ❌ Storage upload error: {result.error.message}")
            raise Exception(result.error.message)

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}"
        logger.info(f"[Supabase] ✅ File uploaded: {public_url}")

        return public_url

    except Exception as e:
        logger.error(f"[Supabase] ❌ Failed to upload to storage: {e}")
        raise


# 🔗 Generate signed URL for private or time-limited access
def generate_signed_url(bucket: str, path: str, expires_in: int = 3600):
    try:
        result = supabase.storage.from_(bucket).create_signed_url(
            path=path,
            expires_in=expires_in
        )

        if hasattr(result, "error") and result.error:
            logger.error(f"[Supabase] ❌ Signed URL error: {result.error.message}")
            raise Exception(result.error.message)

        signed_url = result.get("signedURL")
        logger.info(f"[Supabase] 🔗 Signed URL generated: {signed_url}")

        return signed_url

    except Exception as e:
        logger.error(f"[Supabase] ❌ Failed to generate signed URL: {e}")
        raise
