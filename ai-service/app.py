from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from image_processor import ImageProcessor
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = ImageProcessor()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/process")
async def process_image(request: Request):
    data = await request.json()
    image_url = data.get("image_url")

    if not image_url:
        raise HTTPException(status_code=400, detail="Missing image_url")

    try:
        output_url = processor.process(image_url)
        return {"output_url": output_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/processed/{filename}")
def get_processed_image(filename: str):
    file_path = f"./processed/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)
