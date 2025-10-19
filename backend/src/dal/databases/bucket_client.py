import os
import uuid
from typing import Optional
from minio import Minio
from minio.error import S3Error
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

class BucketClient:
    def __init__(self):
        # MinIO configuration
        self.endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
        self.access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
        self.secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
        self.bucket_name = os.getenv('MINIO_BUCKET_NAME', 'protocols')
        self.secure = os.getenv('MINIO_SECURE', 'false').lower() == 'true'
        
        # Initialize MinIO client
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.info(f"Bucket already exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
            raise
    
    def upload_file(self, file_content: bytes, filename: str, content_type: str) -> str:
        """
        Upload a file to MinIO and return the object URL
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type of the file
            
        Returns:
            str: Object URL for the uploaded file
        """
        try:
            # Generate unique object name
            file_extension = filename.split('.')[-1] if '.' in filename else ''
            object_name = f"{uuid.uuid4()}.{file_extension}"
            
            # Upload file - wrap bytes in BytesIO for MinIO client
            file_data = BytesIO(file_content)
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                length=len(file_content),
                content_type=content_type
            )
            
            # Generate object URL - use external endpoint for frontend access
            external_endpoint = os.getenv('MINIO_EXTERNAL_ENDPOINT', 'localhost:9000')
            object_url = f"{'https' if self.secure else 'http'}://{external_endpoint}/{self.bucket_name}/{object_name}"
            
            logger.info(f"Successfully uploaded file: {object_name}")
            return object_url
            
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def download_file(self, object_url: str) -> bytes:
        """
        Download a file from MinIO using object URL
        
        Args:
            object_url: Full URL of the object
            
        Returns:
            bytes: File content
        """
        try:
            # Extract object name from URL
            object_name = object_url.split(f"/{self.bucket_name}/")[-1]
            
            # Download file
            response = self.client.get_object(self.bucket_name, object_name)
            file_content = response.read()
            response.close()
            response.release_conn()
            
            logger.info(f"Successfully downloaded file: {object_name}")
            return file_content
            
        except S3Error as e:
            logger.error(f"Error downloading file: {e}")
            raise Exception(f"Failed to download file: {str(e)}")
    
    def delete_file(self, object_url: str) -> bool:
        """
        Delete a file from MinIO using object URL
        
        Args:
            object_url: Full URL of the object
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Extract object name from URL
            object_name = object_url.split(f"/{self.bucket_name}/")[-1]
            
            # Delete file
            self.client.remove_object(self.bucket_name, object_name)
            
            logger.info(f"Successfully deleted file: {object_name}")
            return True
            
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def get_file_info(self, object_url: str) -> Optional[dict]:
        """
        Get file information from MinIO using object URL
        
        Args:
            object_url: Full URL of the object
            
        Returns:
            dict: File information or None if not found
        """
        try:
            # Extract object name from URL
            object_name = object_url.split(f"/{self.bucket_name}/")[-1]
            
            # Get object stats
            stat = self.client.stat_object(self.bucket_name, object_name)
            
            return {
                'object_name': object_name,
                'size': stat.size,
                'content_type': stat.content_type,
                'last_modified': stat.last_modified,
                'etag': stat.etag
            }
            
        except S3Error as e:
            logger.error(f"Error getting file info: {e}")
            return None
