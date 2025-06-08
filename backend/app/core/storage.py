from typing import Optional, BinaryIO
import os
import shutil
from pathlib import Path
from app.core.config import settings
from fastapi.staticfiles import StaticFiles
import logging

logger = logging.getLogger(__name__)

class LocalStorageClient:
    def __init__(self):
        self.storage_dir = Path(settings.STORAGE_PATH)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.bucket = settings.STORAGE_BUCKET

    def upload_file(self, file: BinaryIO, path: str) -> str:
        """Upload a file to local storage and return its path"""
        try:
            file_path = self.storage_dir / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file, f)
            
            return self.get_public_url(path)
        except Exception as e:
            logger.error(f"Error uploading file to local storage: {str(e)}")
            raise

    def get_public_url(self, path: str) -> str:
        """Get local file URL"""
        return f"{settings.STORAGE_PUBLIC_URL}/{path}"

    def delete_file(self, path: str) -> bool:
        """Delete a file from local storage"""
        try:
            file_path = self.storage_dir / path
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as e:
            logger.error(f"Error deleting file from local storage: {str(e)}")
            return False

# Create storage client based on provider
if settings.STORAGE_PROVIDER == "local":
    storage_client = LocalStorageClient()
else:
    # For now, fall back to local storage in development
    logger.warning(f"Storage provider '{settings.STORAGE_PROVIDER}' not implemented, falling back to local storage")
    storage_client = LocalStorageClient()

# Mount storage directory in FastAPI app
def mount_storage(app):
    """Mount storage directory in FastAPI app for serving files"""
    try:
        app.mount("/storage", StaticFiles(directory=settings.STORAGE_PATH), name="storage")
    except Exception as e:
        logger.error(f"Error mounting storage directory: {str(e)}")
        raise 