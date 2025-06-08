from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from rembg import remove, new_session
import io
from PIL import Image
import numpy as np
import cv2
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Image Processing Service")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/remove-background")
async def remove_background(
    file: UploadFile = File(...),
    model_name: Optional[str] = "u2net"  # Default model
):
    """Remove background from image using rembg"""
    try:
        # Read and validate image
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")

        # Convert to PIL Image
        image = Image.open(io.BytesIO(contents))
        
        # Create session with specified model
        session = new_session(model_name)
        
        # Remove background
        output = remove(image, session=session)
        
        # Convert back to bytes
        img_byte_arr = io.BytesIO()
        output.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return Response(content=img_byte_arr.getvalue(), media_type="image/png")
    except Exception as e:
        logger.error(f"Background removal failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/enhance")
async def enhance_image(
    file: UploadFile = File(...),
    scale_factor: float = 2.0
):
    """Enhance image quality"""
    try:
        # Read image
        contents = await file.read()
        img = Image.open(io.BytesIO(contents))
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Apply basic enhancement
        enhanced = cv2.detailEnhance(img_array, sigma_s=10, sigma_r=0.15)
        
        # Resize image
        height, width = enhanced.shape[:2]
        new_height = int(height * scale_factor)
        new_width = int(width * scale_factor)
        enhanced = cv2.resize(enhanced, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        
        # Convert back to PIL Image
        enhanced_img = Image.fromarray(enhanced)
        
        # Save to bytes
        img_byte_arr = io.BytesIO()
        enhanced_img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        return Response(content=img_byte_arr, media_type="image/png")
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/smart-crop")
async def smart_crop(
    file: UploadFile = File(...),
    width: int = 300,
    height: int = 300
):
    """Smart crop image using energy map"""
    try:
        # Read image
        contents = await file.read()
        img = Image.open(io.BytesIO(contents))
        img_array = np.array(img)
        
        # Calculate energy map
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        energy_map = cv2.Sobel(gray, cv2.CV_64F, 1, 1)
        
        # Find the region with lowest energy
        h, w = img_array.shape[:2]
        x = max(0, (w - width) // 2)
        y = max(0, (h - height) // 2)
        
        # Crop the image
        cropped = img_array[y:y+height, x:x+width]
        
        # Convert back to PIL Image
        cropped_img = Image.fromarray(cropped)
        
        # Save to bytes
        img_byte_arr = io.BytesIO()
        cropped_img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        return Response(content=img_byte_arr, media_type="image/png")
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 