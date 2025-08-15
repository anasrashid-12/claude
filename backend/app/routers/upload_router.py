# app/api/upload_router.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Cookie, Form, Depends
from starlette.responses import JSONResponse
import uuid
import os
import jwt
import asyncio
from typing import List, Optional
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

@upload_router.post("/upload")
async def upload_image(
  request: Request,
  file: UploadFile = File(...),
  operation: str = Form(...),
  session: str = Cookie(None),
):
  shop = get_shop_from_cookie(session)
  operation = normalize_operation(operation)

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

    # Optional tiny pause to let storage settle
    await asyncio.sleep(1)
    submit_job_task.delay(image_id, operation, path, shop)

    return JSONResponse(content={
      "id": image_id,
      "status": "queued",
      "remaining_credits": remaining
    }, status_code=202)

  except Exception as e:
    logger.error(f"Upload failed: {e}")
    # Refund if we failed after deducting credits
    try:
      add_shop_credits(shop, 1, "Refund: upload failed")
    except Exception:
      pass
    raise HTTPException(status_code=500, detail="Upload failed")

@upload_router.post("/upload-multiple")
async def upload_multiple_images(
  request: Request,
  files: List[UploadFile] = File(...),
  operation: str = Form(...),
  session: str = Cookie(None),
):
  shop = get_shop_from_cookie(session)
  operation = normalize_operation(operation)

  if not files:
    raise HTTPException(status_code=400, detail="No files provided")

  uploaded_results = []
  failed_files = []

  for file in files:
    try:
      filename = f"{uuid.uuid4()}.png"
      path = f"{shop}/upload/{filename}"
      file_content = await file.read()

      upload_result = supabase.storage.from_(SUPABASE_BUCKET).upload(
        path=path,
        file=file_content,
        file_options={"content-type": file.content_type},
      )
      if hasattr(upload_result, "error") and upload_result.error:
        raise Exception(f"Upload failed: {upload_result.error.message}")

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

      try:
        remaining = deduct_shop_credit(shop, amount=1)
      except ValueError:
        # Remove DB row if we can't afford it
        supabase.table("images").delete().eq("id", image_id).execute()
        failed_files.append(file.filename)
        continue

      try:
        task_result = submit_job_task.delay(image_id, operation, path, shop)
        celery_job_id = task_result.id
      except Exception:
        add_shop_credits(shop, 1, "Refund: queue failed")
        supabase.table("images").delete().eq("id", image_id).execute()
        failed_files.append(file.filename)
        continue

      uploaded_results.append({
        "id": image_id,
        "filename": file.filename,
        "status": "queued",
        "celery_job_id": celery_job_id,
        "remaining_credits": remaining
      })

    except Exception as e:
      logger.error(f"Failed to process file {file.filename}: {e}")
      failed_files.append(file.filename)

  if not uploaded_results:
    raise HTTPException(status_code=500, detail="All uploads failed.")

  return JSONResponse(content={
    "success": uploaded_results,
    "failed": failed_files
  }, status_code=202)

# 🔎 NEW: simple status endpoint for polling
@upload_router.get("/images/{image_id}")
async def get_image_status(image_id: str, session: str = Cookie(None)):
  # Optional: validate user owns this image via shop in token
  shop = get_shop_from_cookie(session)
  result = supabase.table("images").select("*").eq("id", image_id).eq("shop", shop).single().execute()
  if hasattr(result, "error") and result.error:
    raise HTTPException(status_code=404, detail="Not found")
  data = result.data or {}
  return {
    "id": data.get("id"),
    "status": data.get("status"),
    "operation": data.get("operation"),
    "filename": data.get("filename"),
    "processed_path": data.get("processed_path"),
    "error_message": data.get("error_message"),
  }
