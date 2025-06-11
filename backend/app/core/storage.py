from typing import Optional, BinaryIO
import os
import shutil
from pathlib import Path
from app.core.config import settings
from fastapi.staticfiles import StaticFiles
import logging
import boto3
from botocore.exceptions import ClientError
from .database import get_supabase_client

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

def upload_file(
    file_bytes: bytes,
    filename: str,
    content_type: str = "application/octet-stream",
    bucket: Optional[str] = None
) -> str:
    """
    Upload a file to storage
    
    :param file_bytes: File content as bytes
    :param filename: Name of the file
    :param content_type: MIME type of the file
    :param bucket: Optional bucket name for S3
    :return: URL of the uploaded file
    """
    if settings.STORAGE_PROVIDER == "supabase":
        return _upload_to_supabase(file_bytes, filename, content_type)
    elif settings.STORAGE_PROVIDER == "s3":
        return _upload_to_s3(file_bytes, filename, content_type, bucket)
    else:
        raise ValueError(f"Unsupported storage provider: {settings.STORAGE_PROVIDER}")

def _upload_to_supabase(file_bytes: bytes, filename: str, content_type: str) -> str:
    """
    Upload a file to Supabase Storage
    
    :param file_bytes: File content as bytes
    :param filename: Name of the file
    :param content_type: MIME type of the file
    :return: URL of the uploaded file
    """
    try:
        client = get_supabase_client()
        bucket_name = "images"  # You can make this configurable
        
        # Create bucket if it doesn't exist
        try:
            client.storage.create_bucket(bucket_name)
        except Exception:
            pass  # Bucket might already exist
        
        # Upload file
        result = client.storage.from_(bucket_name).upload(
            path=filename,
            file=file_bytes,
            file_options={"content-type": content_type}
        )
        
        # Get public URL
        url = client.storage.from_(bucket_name).get_public_url(filename)
        return url
        
    except Exception as e:
        logger.error(f"Failed to upload file to Supabase Storage: {e}")
        raise

def _upload_to_s3(
    file_bytes: bytes,
    filename: str,
    content_type: str,
    bucket: Optional[str] = None
) -> str:
    """
    Upload a file to AWS S3
    
    :param file_bytes: File content as bytes
    :param filename: Name of the file
    :param content_type: MIME type of the file
    :param bucket: Optional bucket name
    :return: URL of the uploaded file
    """
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        bucket_name = bucket or os.getenv('AWS_S3_BUCKET')
        if not bucket_name:
            raise ValueError("S3 bucket name not provided")
        
        # Upload file
        s3_client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=file_bytes,
            ContentType=content_type
        )
        
        # Generate URL
        url = f"https://{bucket_name}.s3.amazonaws.com/{filename}"
        return url
        
    except Exception as e:
        logger.error(f"Failed to upload file to S3: {e}")
        raise

def delete_file(filename: str, bucket: Optional[str] = None) -> bool:
    """
    Delete a file from storage
    
    :param filename: Name of the file to delete
    :param bucket: Optional bucket name
    :return: True if deleted successfully
    """
    try:
        if settings.STORAGE_PROVIDER == "supabase":
            client = get_supabase_client()
            bucket_name = "images"  # You can make this configurable
            client.storage.from_(bucket_name).remove([filename])
            return True
            
        elif settings.STORAGE_PROVIDER == "s3":
            s3_client = boto3.client('s3')
            bucket_name = bucket or os.getenv('AWS_S3_BUCKET')
            if not bucket_name:
                raise ValueError("S3 bucket name not provided")
                
            s3_client.delete_object(
                Bucket=bucket_name,
                Key=filename
            )
            return True
            
        else:
            raise ValueError(f"Unsupported storage provider: {settings.STORAGE_PROVIDER}")
            
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        return False 