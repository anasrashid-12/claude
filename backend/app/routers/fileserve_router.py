from fastapi import APIRouter, HTTPException
from app.services.supabase_service import supabase
import os

fileserve_router = APIRouter()

BUCKET_NAME = "makeit3d-public"

@fileserve_router.get("/signed-url/{filename}")
def generate_signed_url(filename: str):
    try:
        signed = supabase.storage.from_(BUCKET_NAME).create_signed_url(
            path=filename,
            expires_in=3600  # 1 hour
        )

        if signed.get("error"):
            raise HTTPException(status_code=500, detail="Failed to generate signed URL")

        return {
            "signed_url": signed.get("signedURL"),
            "expires_in": 3600,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating signed URL: {str(e)}")


__all__ = ["fileserve_router"]
