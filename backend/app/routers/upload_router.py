from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Cookie, Form
from starlette.responses import JSONResponse
import uuid
import os
import jwt
import traceback
import asyncio 
from app.logging_config import logger
from app.services.supabase_service import supabase
from app.tasks.image_tasks import submit_job_task
from app.services.supabase_service import deduct_shop_credit, get_shop_credits

upload_router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "makeit3d-public")
JWT_SECRET = os.getenv("JWT_SECRET")

@upload_router.post("/upload")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    operation: str = Form(...),
    session: str = Cookie(None),
):
    if not session:
        raise HTTPException(status_code=401, detail="No session token found")

    try:
        payload = jwt.decode(session, JWT_SECRET, algorithms=["HS256"])
        shop = payload.get("shop")
    except Exception as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(status_code=401, detail="Invalid session token")

    try:
        remaining = deduct_shop_credit(shop, amount=1)
        logger.info(f"[Credits] Deducted 1 credit for {shop}, remaining: {remaining}")
    except ValueError as e:
        logger.warning(f"[Credits] Upload blocked for {shop} - {str(e)}")
        raise HTTPException(
            status_code=402,
            detail={"message": "Not enough credits. Please purchase more to continue.", "remaining_credits": 0}
        )

    filename = f"{uuid.uuid4()}.png"
    path = f"{shop}/upload/{filename}"

    try:
        file_content = await file.read()
        logger.info(f"Uploading file for shop {shop}: {filename} → {path}")

        upload_result = supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=path,
            file=file_content,
            file_options={"content-type": file.content_type},
        )

        if hasattr(upload_result, "error") and upload_result.error:
            raise Exception(f"Upload failed to Supabase storage: {upload_result.error.message}")

        insert_response = supabase.table("images").insert({
            "shop": shop,
            "original_path": path,
            "status": "pending",
            "operation": operation,
            "filename": file.filename,
        }).execute()

        if not insert_response.data:
            raise Exception("Image insert failed in Supabase")

        image_id = insert_response.data[0]["id"]

        await asyncio.sleep(5)
        submit_job_task.delay(image_id, operation, path, shop)

        return JSONResponse(content={
            "id": image_id,
            "status": "queued",
            "remaining_credits": remaining
        }, status_code=202)

    except Exception as e:
        logger.error(f"Upload failed: {e}\n{traceback.format_exc()}")
        # If upload fails, refund credit
        from app.services.supabase_service import add_shop_credits
        add_shop_credits(shop, 1, "Refund: upload failed")
        raise HTTPException(status_code=500, detail="Upload failed")
