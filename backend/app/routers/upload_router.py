from fastapi import APIRouter, UploadFile, File, HTTPException, Cookie, Form
from starlette.responses import JSONResponse
import uuid
import os
import jwt
from typing import Optional
from app.logging_config import logger
from app.services.supabase_service import supabase
from app.tasks.image_tasks import submit_job_task
from app.services.supabase_service import deduct_shop_credit, add_shop_credits

upload_router = APIRouter()

SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "makeit3d-public")
JWT_SECRET = os.getenv("JWT_SECRET")


def normalize_operation(op: str) -> str:
    mapping = {
        "remove-background": "remove-bg",
        "remove_bg": "remove-bg",
        "remove-bg": "remove-bg",
        "upscale": "upscale",
        "downscale": "downscale",
    }
    return mapping.get(op, op)


def get_shop_from_cookie(session: Optional[str]) -> str:
    if not session:
        raise HTTPException(status_code=401, detail="No session token found")
    try:
        payload = jwt.decode(session, JWT_SECRET, algorithms=["HS256"])
        shop = payload.get("shop")
        if not shop:
            raise Exception("Missing shop in token")
        return shop
    except Exception as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(status_code=401, detail="Invalid session token")


async def process_single_file(file: UploadFile, operation: str, shop: str):
    """Upload one file, insert DB record, deduct credit, and queue Celery job."""
    filename = f"{uuid.uuid4()}.png"
    path = f"{shop}/upload/{filename}"

    # Read file content
    file_content = await file.read()

    # Upload to Supabase Storage
    try:
        upload_result = supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=path,
            file=file_content,
            file_options={"content-type": file.content_type},
        )
        # access attributes correctly
        if upload_result.error:
            raise Exception(f"Supabase upload failed: {upload_result.error}")
        if not upload_result.data:
            raise Exception("Supabase upload failed: No data returned")
        logger.info(f"Upload succeeded for {path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase upload failed: {e}")

    # Insert DB row
    try:
        insert_response = supabase.table("images").insert({
            "shop": shop,
            "original_path": path,
            "status": "pending",
            "operation": operation,
            "filename": file.filename,
        }).execute()

        if insert_response.status_code not in (200, 201) or not insert_response.data:
            raise Exception(f"Image insert failed: {insert_response.data}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database insert failed: {e}")

    image_id = insert_response.data[0]["id"]

    # Deduct credit
    try:
        remaining = deduct_shop_credit(shop, amount=1)
    except ValueError:
        supabase.table("images").delete().eq("id", image_id).execute()
        raise HTTPException(status_code=402, detail={
            "message": "Not enough credits. Please purchase more to continue.",
            "remaining_credits": 0
        })

    # Queue job
    try:
        task_result = submit_job_task.delay(image_id, operation, path, shop)
        celery_job_id = task_result.id
    except Exception as e:
        add_shop_credits(shop, 1, "Refund: queue failed")
        supabase.table("images").delete().eq("id", image_id).execute()
        raise HTTPException(status_code=500, detail=f"Queueing job failed: {e}")

    return {
        "id": image_id,
        "filename": file.filename,
        "status": "queued",
        "celery_job_id": celery_job_id,
        "remaining_credits": remaining
    }


@upload_router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    operation: str = Form(...),
    session: str = Cookie(None),
):
    shop = get_shop_from_cookie(session)
    operation = normalize_operation(operation)

    try:
        result = await process_single_file(file, operation, shop)
        return JSONResponse(content=result, status_code=202)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@upload_router.get("/images/{image_id}")
async def get_image_status(image_id: str, session: str = Cookie(None)):
    shop = get_shop_from_cookie(session)
    try:
        result = supabase.table("images") \
            .select("*") \
            .eq("id", image_id) \
            .eq("shop", shop) \
            .single() \
            .execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    if not result.get("data"):
        raise HTTPException(status_code=404, detail="Not found")

    data = result["data"]
    return {
        "id": data.get("id"),
        "status": data.get("status"),
        "operation": data.get("operation"),
        "filename": data.get("filename"),
        "processed_path": data.get("processed_path"),
        "error_message": data.get("error_message"),
    }
