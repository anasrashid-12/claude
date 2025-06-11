import cv2
import numpy as np
from PIL import Image, ImageEnhance
import io
from rembg import remove
from skimage import exposure
import torch
import torchvision.transforms as transforms
from typing import Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Image processing class with various image manipulation operations."""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
    def _load_image(self, image_data: bytes) -> Tuple[np.ndarray, Image.Image]:
        """Load image from bytes into both OpenCV and PIL formats."""
        # Convert bytes to PIL Image
        pil_image = Image.open(io.BytesIO(image_data))
        
        # Convert PIL Image to OpenCV format
        cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return cv_image, pil_image

    def _save_image(self, image: np.ndarray, format: str = 'JPEG') -> bytes:
        """Convert OpenCV image to bytes in specified format."""
        # Convert OpenCV image to PIL Image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # Save to bytes
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format=format)
        return img_byte_arr.getvalue()

    def remove_background(self, image_data: bytes) -> bytes:
        """Remove background from image using rembg."""
        try:
            # Use rembg to remove background
            result = remove(image_data)
            return result
            
        except Exception as e:
            raise Exception(f"Background removal failed: {str(e)}")

    def enhance_image(self, image_data: bytes, params: Optional[Dict[str, float]] = None) -> bytes:
        """Enhance image with specified parameters."""
        try:
            # Load image
            _, pil_image = self._load_image(image_data)
            
            # Default enhancement parameters
            params = params or {
                'brightness': 1.0,
                'contrast': 1.0,
                'sharpness': 1.0,
                'color': 1.0
            }
            
            # Apply enhancements
            if 'brightness' in params:
                pil_image = ImageEnhance.Brightness(pil_image).enhance(params['brightness'])
            if 'contrast' in params:
                pil_image = ImageEnhance.Contrast(pil_image).enhance(params['contrast'])
            if 'sharpness' in params:
                pil_image = ImageEnhance.Sharpness(pil_image).enhance(params['sharpness'])
            if 'color' in params:
                pil_image = ImageEnhance.Color(pil_image).enhance(params['color'])
            
            # Convert back to bytes
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
            
        except Exception as e:
            raise Exception(f"Image enhancement failed: {str(e)}")

    def resize_image(self, image_data: bytes, target_size: Tuple[int, int]) -> bytes:
        """Resize image to target size while maintaining aspect ratio."""
        try:
            # Load image
            cv_image, _ = self._load_image(image_data)
            
            # Calculate new dimensions maintaining aspect ratio
            h, w = cv_image.shape[:2]
            target_w, target_h = target_size
            aspect = w / h
            
            if target_w / target_h > aspect:
                new_w = int(target_h * aspect)
                new_h = target_h
            else:
                new_w = target_w
                new_h = int(target_w / aspect)
            
            # Resize image
            resized = cv2.resize(cv_image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
            
            return self._save_image(resized)
            
        except Exception as e:
            raise Exception(f"Image resize failed: {str(e)}")

    def optimize_image(self, image_data: bytes, quality: int = 85) -> bytes:
        """Optimize image for web delivery."""
        try:
            # Load image
            _, pil_image = self._load_image(image_data)
            
            # Convert to RGB if necessary
            if pil_image.mode in ('RGBA', 'P'):
                pil_image = pil_image.convert('RGB')
            
            # Save with optimization
            img_byte_arr = io.BytesIO()
            pil_image.save(
                img_byte_arr,
                format='JPEG',
                quality=quality,
                optimize=True
            )
            return img_byte_arr.getvalue()
            
        except Exception as e:
            raise Exception(f"Image optimization failed: {str(e)}")

    def auto_crop(self, image_data: bytes) -> bytes:
        """Automatically crop image to remove empty spaces"""
        try:
            cv_image, _ = self._load_image(image_data)
            
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Find non-empty region
            coords = cv2.findNonZero(gray)
            x, y, w, h = cv2.boundingRect(coords)
            
            # Crop image
            cropped = cv_image[y:y+h, x:x+w]
            return self._save_image(cropped)
            
        except Exception as e:
            logger.error(f"Auto-cropping failed: {str(e)}")
            raise 