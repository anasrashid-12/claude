from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.services.supabase_service import supabase
from app.services.signed_url_util import get_signed_url  
import httpx
import logging

fileserve_router = APIRouter()
logger = logging.getLogger("fileserve_router")


@fileserve_router.get("/fileserve/signed-url/{path:path}")
def generate_signed_url(path: str):
    try:
        signed_url = get_signed_url(path)
        return {"signed_url": signed_url}
    except Exception as e:
        logger.warning(f"Failed to generate signed URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate signed URL")


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
