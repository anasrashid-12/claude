import cv2
import numpy as np
from PIL import Image
import io
from rembg import remove
from skimage import exposure
import torch
import torchvision.transforms as transforms
from typing import Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
    def _load_image(self, image_data: bytes) -> Tuple[np.ndarray, Image.Image]:
        """Load image from bytes into both OpenCV and PIL formats"""
        # Load as PIL Image
        pil_image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert to OpenCV format
        cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return cv_image, pil_image

    def _save_image(self, image: np.ndarray, format: str = 'JPEG') -> bytes:
        """Convert OpenCV image to bytes"""
        # Convert from BGR to RGB
        if len(image.shape) == 3:  # Color image
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(image)
        
        # Save to bytes
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format=format)
        return img_byte_arr.getvalue()

    def remove_background(self, image_data: bytes) -> bytes:
        """Remove background from image using rembg"""
        try:
            # Load image as PIL Image
            input_pil = Image.open(io.BytesIO(image_data))
            
            # Remove background
            output_pil = remove(input_pil)
            
            # Convert to bytes
            output_bytes = io.BytesIO()
            output_pil.save(output_bytes, format='PNG')
            return output_bytes.getvalue()
            
        except Exception as e:
            logger.error(f"Background removal failed: {str(e)}")
            raise

    def enhance_image(self, image_data: bytes, 
                     params: Dict[str, float] = None) -> bytes:
        """Enhance image quality with various adjustments"""
        if params is None:
            params = {
                'contrast': 1.2,
                'brightness': 1.1,
                'sharpness': 1.5
            }
        
        try:
            cv_image, _ = self._load_image(image_data)
            
            # Adjust contrast and brightness
            cv_image = exposure.adjust_gamma(cv_image, params['contrast'])
            cv_image = cv2.convertScaleAbs(cv_image, 
                                         alpha=params['brightness'], 
                                         beta=0)
            
            # Apply sharpening
            kernel = np.array([[-1,-1,-1],
                             [-1, 9,-1],
                             [-1,-1,-1]]) * params['sharpness']
            cv_image = cv2.filter2D(cv_image, -1, kernel)
            
            return self._save_image(cv_image)
            
        except Exception as e:
            logger.error(f"Image enhancement failed: {str(e)}")
            raise

    def resize_image(self, image_data: bytes, 
                    target_size: Tuple[int, int], 
                    maintain_aspect: bool = True) -> bytes:
        """Resize image to target size"""
        try:
            cv_image, _ = self._load_image(image_data)
            
            if maintain_aspect:
                # Calculate new dimensions maintaining aspect ratio
                h, w = cv_image.shape[:2]
                target_w, target_h = target_size
                aspect = w / h
                
                if target_w / target_h > aspect:
                    target_w = int(target_h * aspect)
                else:
                    target_h = int(target_w / aspect)
            
            resized = cv2.resize(cv_image, (target_w, target_h), 
                               interpolation=cv2.INTER_LANCZOS4)
            return self._save_image(resized)
            
        except Exception as e:
            logger.error(f"Image resizing failed: {str(e)}")
            raise

    def optimize_image(self, image_data: bytes, 
                      quality: int = 85, 
                      format: str = 'JPEG') -> bytes:
        """Optimize image for web delivery"""
        try:
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Save with optimization
            output = io.BytesIO()
            pil_image.save(output, 
                          format=format, 
                          quality=quality, 
                          optimize=True)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Image optimization failed: {str(e)}")
            raise

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