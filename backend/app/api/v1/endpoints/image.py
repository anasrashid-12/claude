from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.core.celery_app import celery_app
from app.tasks.image_processing import process_image
from app.database import Database
from typing import Optional
import uuid

router = APIRouter()

@router.post("/process/{process_type}")
async def process_image_endpoint(
    process_type: str,
    file: UploadFile = File(...),
    store_id: Optional[str] = Form(None)
):
    """
    Process an image with the specified processing type.
    """
    try:
        # Generate a unique ID for this processing task
        task_id = str(uuid.uuid4())
        
        # Save the original file temporarily
        file_content = await file.read()
        file_path = f"/tmp/{task_id}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Start the Celery task
        task = celery_app.send_task(
            "app.tasks.image_processing.process_image",
            args=[file_path, process_type, task_id, store_id],
            queue="image_processing"
        )

        # Store task information in the database
        db = Database()
        await db.client.from_("processing_tasks").insert({
            "id": task_id,
            "store_id": store_id,
            "original_filename": file.filename,
            "process_type": process_type,
            "status": "processing",
            "celery_task_id": task.id
        }).execute()

        return JSONResponse({
            "task_id": task_id,
            "status": "processing",
            "message": "Image processing started"
        })

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image: {str(e)}"
        ) 