from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from app.services.supabase_service import supabase
import httpx
import logging

fileserve_router = APIRouter()
logger = logging.getLogger("fileserve_router")

BUCKET_NAME = "makeit3d-public"

def get_signed_url(path: str, expires_in: int = 60 * 60 * 24 * 7) -> str:
    try:
        result = supabase.storage.from_(BUCKET_NAME).create_signed_url(
            path=path,
            expires_in=expires_in
        )
        signed_url = result.get("signedURL") or result.get("signed_url")
        if not signed_url:
            logger.warning("Signed URL not found in response")
            raise HTTPException(status_code=500, detail="Failed to generate signed URL")
        return signed_url
    except Exception as e:
        logger.warning(f"Signed URL generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Signed URL error: {str(e)}")


@fileserve_router.get("/fileserve/signed-url/{path:path}")
def generate_signed_url(path: str):
    signed_url = get_signed_url(path)
    return {"signed_url": signed_url}


@fileserve_router.get("/fileserve/download")
async def download_image(path: str = Query(...)):
    try:
        signed_url = get_signed_url(path)

        async with httpx.AsyncClient() as client:
            resp = await client.get(signed_url)

        if resp.status_code != 200:
            logger.warning(f"Supabase file fetch failed: {resp.status_code}")
            raise HTTPException(status_code=404, detail="Image not found")

        filename = path.split("/")[-1]
        return StreamingResponse(
            iter([resp.content]),
            media_type=resp.headers.get("content-type", "application/octet-stream"),
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except Exception as e:
        logger.warning(f"Download failed: {e}")
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")
