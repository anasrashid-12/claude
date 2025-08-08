from fastapi import HTTPException
from app.services.supabase_service import supabase
import logging

logger = logging.getLogger("signed_url_util")
BUCKET_NAME = "makeit3d-public"

def get_signed_url(path: str, expires_in: int = 60 * 60 * 24 * 7) -> str:
    try:
        result = supabase.storage.from_(BUCKET_NAME).create_signed_url(
            path=path,
            expires_in=expires_in
        )
        signed_url = result.get("signedURL") or result.get("signed_url")
        if not signed_url:
            raise Exception("No signed URL in response")
        return signed_url
    except Exception as e:
        logger.warning(f"Signed URL error: {e}")
        raise HTTPException(status_code=500, detail=f"Signed URL error: {str(e)}")
