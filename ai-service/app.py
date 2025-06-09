from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from image_processor import ImageProcessor
import logging
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Shopify AI Image Service")

# Initialize image processor
processor = ImageProcessor()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-image-processor"}

@app.post("/process")
async def process_image(
    file: UploadFile = File(...),
    process_type: str = "enhance",
    params: dict = None
):
    """
    Process an uploaded image
    
    Args:
        file: The image file to process
        process_type: Type of processing to perform
        params: Additional parameters for processing
    """
    try:
        # Read image data
        image_data = await file.read()
        
        # Process image based on type
        if process_type == "background_removal":
            result = processor.remove_background(image_data)
        elif process_type == "enhance":
            result = processor.enhance_image(image_data, params)
        elif process_type == "resize":
            if not params or 'size' not in params:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Size parameter required for resize"}
                )
            result = processor.resize_image(
                image_data,
                params['size'],
                params.get('maintain_aspect', True)
            )
        elif process_type == "optimize":
            result = processor.optimize_image(
                image_data,
                quality=params.get('quality', 85) if params else 85
            )
        elif process_type == "auto_crop":
            result = processor.auto_crop(image_data)
        else:
            return JSONResponse(
                status_code=400,
                content={"error": f"Unknown process type: {process_type}"}
            )
            
        return {
            "status": "success",
            "process_type": process_type,
            "processed_image_data": result
        }
        
    except Exception as e:
        logger.error(f"Image processing failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Processing failed: {str(e)}"}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 