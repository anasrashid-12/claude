from os import environ
import boto3
from botocore.config import Config
from typing import Optional, BinaryIO
import mimetypes

class CDNService:
    def __init__(self):
        # Initialize S3 client for Cloudflare R2
        self.s3_client = boto3.client(
            's3',
            endpoint_url=environ.get('R2_ENDPOINT_URL'),
            aws_access_key_id=environ.get('R2_ACCESS_KEY_ID'),
            aws_secret_access_key=environ.get('R2_SECRET_ACCESS_KEY'),
            config=Config(
                region_name='auto',
                signature_version='v4',
                retries={'max_attempts': 3}
            )
        )
        self.bucket_name = environ.get('R2_BUCKET_NAME')
        self.cdn_domain = environ.get('CDN_DOMAIN')

    async def upload_image(self, file_path: str, file_content: BinaryIO, content_type: Optional[str] = None) -> str:
        """Upload an image to CDN and return its URL"""
        if not content_type:
            content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

        try:
            # Upload to R2
            self.s3_client.upload_fileobj(
                file_content,
                self.bucket_name,
                file_path,
                ExtraArgs={
                    'ContentType': content_type,
                    'CacheControl': 'public, max-age=31536000',  # 1 year cache
                    'ACL': 'public-read'
                }
            )

            # Return CDN URL
            return f"https://{self.cdn_domain}/{file_path}"

        except Exception as e:
            raise Exception(f"Failed to upload image to CDN: {str(e)}")

    async def delete_image(self, file_path: str) -> bool:
        """Delete an image from CDN"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to delete image from CDN: {str(e)}")

    async def get_image_url(self, file_path: str) -> str:
        """Get CDN URL for an image"""
        try:
            # Check if object exists
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            return f"https://{self.cdn_domain}/{file_path}"
        except:
            raise Exception("Image not found in CDN")

cdn_service = CDNService() 