import cv2
import numpy as np
from PIL import Image, ImageEnhance
import io
from rembg import remove
import torch
import logging
from typing import Tuple, Optional, Dict

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")

    def _load_image(self, image_data: bytes) -> Tuple[np.ndarray, Image.Image]:
        pil_image = Image.open(io.BytesIO(image_data)).convert("RGB")
        cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        return cv_image, pil_image

    def _save_image(self, image: np.ndarray, format: str = 'JPEG') -> bytes:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format=format)
        return img_byte_arr.getvalue()

    def remove_background(self, image_data: bytes) -> bytes:
        try:
            return remove(image_data)
        except Exception as e:
            logger.error(f"Background removal failed: {e}")
            raise

    def enhance_image(self, image_data: bytes, params: Optional[Dict[str, float]] = None) -> bytes:
        try:
            _, pil_image = self._load_image(image_data)
            params = params or {}
            if 'brightness' in params:
                pil_image = ImageEnhance.Brightness(pil_image).enhance(params['brightness'])
            if 'contrast' in params:
                pil_image = ImageEnhance.Contrast(pil_image).enhance(params['contrast'])
            if 'sharpness' in params:
                pil_image = ImageEnhance.Sharpness(pil_image).enhance(params['sharpness'])
            if 'color' in params:
                pil_image = ImageEnhance.Color(pil_image).enhance(params['color'])

            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
        except Exception as e:
            logger.error(f"Enhancement failed: {e}")
            raise

    def resize_image(self, image_data: bytes, target_size: Tuple[int, int]) -> bytes:
        try:
            cv_image, _ = self._load_image(image_data)
            h, w = cv_image.shape[:2]
            target_w, target_h = target_size
            aspect = w / h

            if target_w / target_h > aspect:
                new_w = int(target_h * aspect)
                new_h = target_h
            else:
                new_w = target_w
                new_h = int(target_w / aspect)

            resized = cv2.resize(cv_image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
            return self._save_image(resized)
        except Exception as e:
            logger.error(f"Resize failed: {e}")
            raise

    def optimize_image(self, image_data: bytes, quality: int = 85) -> bytes:
        try:
            _, pil_image = self._load_image(image_data)
            if pil_image.mode in ('RGBA', 'P'):
                pil_image = pil_image.convert('RGB')
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='JPEG', quality=quality, optimize=True)
            return img_byte_arr.getvalue()
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            raise

    def auto_crop(self, image_data: bytes) -> bytes:
        try:
            cv_image, _ = self._load_image(image_data)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            coords = cv2.findNonZero(gray)
            if coords is None:
                raise ValueError("No non-zero pixels found.")
            x, y, w, h = cv2.boundingRect(coords)
            cropped = cv_image[y:y+h, x:x+w]
            return self._save_image(cropped)
        except Exception as e:
            logger.error(f"Auto-cropping failed: {e}")
            raise
