# backend/routes/upload.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from utils.auth import verify_jwt
from utils.rate_limiter import rate_limiter
from celery_app import process_image_task
import uuid

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/")
@rate_limiter
async def upload_image(file: UploadFile = File(...), user=Depends(verify_jwt)):
    task_id = str(uuid.uuid4())
    contents = await file.read()
    process_image_task.delay(task_id, contents, file.filename, user['user_id'])
    return {"task_id": task_id, "status": "queued"}

upload_router = APIRouter()

@upload_router.post("/upload")
async def upload_file():
    return {"message": "File uploaded successfully"}


shopify_router = APIRouter()

@shopify_router.get("/shopify")
async def shopify_root():
    return {"message": "Shopify route working"}