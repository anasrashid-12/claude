from PIL import Image
import requests
from io import BytesIO
import uuid
import os

OUTPUT_DIR = "./processed"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ImageProcessor:
    def process(self, image_url: str) -> str:
        response = requests.get(image_url)
        if response.status_code != 200:
            raise Exception("Failed to fetch image from URL")

        image = Image.open(BytesIO(response.content))

        # Example: convert to RGBA and resize
        image = image.convert("RGBA")
        image = image.resize((512, 512))  # Example resize

        filename = f"{uuid.uuid4()}.png"
        output_path = os.path.join(OUTPUT_DIR, filename)
        image.save(output_path)

        return f"http://ai-api:8000/processed/{filename}"
