from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict
import io
from image_processor import ImageProcessor
import logging
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
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

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/process")
async def process_image(
    file: UploadFile = File(...),
    process_type: str = "enhance",
    params: Optional[Dict] = None
):
    """
    Process an image with specified operation.
    
    Args:
        file: Image file to process
        process_type: Type of processing to apply (enhance, background_removal, resize, optimize)
        params: Additional parameters for processing
    """
    try:
        # Read image file
        contents = await file.read()
        
        # Process image based on type
        if process_type == "background_removal":
            result = processor.remove_background(contents)
        elif process_type == "enhance":
            result = processor.enhance_image(contents, params)
        elif process_type == "resize":
            if not params or "target_size" not in params:
                raise HTTPException(status_code=400, detail="Target size required for resize")
            result = processor.resize_image(contents, params["target_size"])
        elif process_type == "optimize":
            result = processor.optimize_image(contents, params.get("quality", 85) if params else 85)
        else:
            raise HTTPException(status_code=400, detail="Invalid process type")
        
        return {
            "status": "success",
            "processed_image": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 