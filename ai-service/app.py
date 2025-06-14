# app.py
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import io
import base64
from image_processor import ImageProcessor
import logging
import uvicorn
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="AI Image Processing Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize image processor
processor = ImageProcessor()

@app.get("/")
async def root():
    return {"message": "AI Image Processing Service is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/process")
async def process_image(
    file: UploadFile = File(...),
    process_type: str = Form(...),
    params: Optional[str] = Form(None)  # params as JSON string
):
    try:
        contents = await file.read()

        # Convert params JSON string to dict
        parsed_params = json.loads(params) if params else {}

        # Dispatch based on process_type
        if process_type == "background_removal":
            result = processor.remove_background(contents)
        elif process_type == "enhance":
            result = processor.enhance_image(contents, parsed_params)
        elif process_type == "resize":
            if "target_size" not in parsed_params:
                raise HTTPException(status_code=400, detail="Target size required for resize")
            result = processor.resize_image(contents, tuple(parsed_params["target_size"]))
        elif process_type == "optimize":
            result = processor.optimize_image(contents, parsed_params.get("quality", 85))
        elif process_type == "auto_crop":
            result = processor.auto_crop(contents)
        else:
            raise HTTPException(status_code=400, detail="Invalid process type")

        encoded_result = base64.b64encode(result).decode("utf-8")

        return {
            "status": "success",
            "processed_image_base64": encoded_result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Processing error")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
