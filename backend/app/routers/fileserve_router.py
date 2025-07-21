from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.services.supabase_service import supabase
import httpx

fileserve_router = APIRouter()

BUCKET_NAME = "makeit3d-public"

@fileserve_router.get("/fileserve/signed-url/{filename:path}")
def generate_signed_url(filename: str):
    try:
        signed = supabase.storage.from_(BUCKET_NAME).create_signed_url(
            path=filename,
            expires_in=3600
        )
        if signed.get("error"):
            raise HTTPException(status_code=500, detail="Failed to generate signed URL")
        return { "signed_url": signed.get("signedURL") }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating signed URL: {str(e)}")


@fileserve_router.get("/fileserve/download")
async def download_image(filename: str = Query(...)):
    try:
        signed = supabase.storage.from_(BUCKET_NAME).create_signed_url(
            path=filename,
            expires_in=300
        )
        if signed.get("error"):
            raise HTTPException(status_code=500, detail="Failed to get signed URL")

        async with httpx.AsyncClient() as client:
            resp = await client.get(signed.get("signedURL"))
            if resp.status_code != 200:
                raise HTTPException(status_code=404, detail="Image not found")

            return StreamingResponse(
                iter([resp.content]),
                media_type=resp.headers.get('content-type', 'application/octet-stream'),
                headers={
                    "Content-Disposition": f'attachment; filename="{filename.split("/")[-1]}"'
                }
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")
