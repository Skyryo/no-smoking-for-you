from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
import uuid
from datetime import datetime
from typing import Optional
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        """Initialize Google Cloud Storage client"""
        try:
            self.client = storage.Client(project=settings.GCP_PROJECT_ID)
            self.bucket = self.client.bucket(settings.GCS_BUCKET_NAME)
            logger.info(f"Storage service initialized for bucket: {settings.GCS_BUCKET_NAME}")
        except Exception as e:
            logger.error(f"Failed to initialize storage service: {e}")
            raise

    async def upload_image(self, file_content: bytes, filename: str, session_id: str, content_type: str) -> str:
        """Upload image to Cloud Storage and return public URL"""
        try:
            # Generate unique blob name
            file_extension = self._get_file_extension(filename)
            blob_name = f"uploads/{session_id}/original{file_extension}"
            
            blob = self.bucket.blob(blob_name)
            
            # Set metadata
            blob.metadata = {
                "originalFilename": filename,
                "sessionId": session_id,
                "uploadedAt": datetime.utcnow().isoformat(),
                "contentType": content_type
            }
            
            # Upload file
            blob.upload_from_string(
                file_content,
                content_type=content_type,
                timeout=30
            )
            
            # Make blob publicly readable
            blob.make_public()
            
            logger.info(f"Image uploaded successfully: {blob_name}")
            return blob.public_url
            
        except GoogleCloudError as e:
            logger.error(f"Cloud Storage error: {e}")
            raise Exception("ファイルの保存に失敗しました")
        except Exception as e:
            logger.error(f"Storage upload error: {e}")
            raise Exception("ファイルの保存に失敗しました")

    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename"""
        if "." in filename:
            return "." + filename.split(".")[-1].lower()
        return ".jpg"  # Default extension

    async def delete_image(self, blob_name: str) -> bool:
        """Delete image from Cloud Storage"""
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            logger.info(f"Image deleted: {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete image {blob_name}: {e}")
            return False

    def get_public_url(self, blob_name: str) -> str:
        """Get public URL for a blob"""
        blob = self.bucket.blob(blob_name)
        return blob.public_url

# Global storage service instance - initialized on demand
_storage_service = None

def get_storage_service() -> StorageService:
    """Get or create storage service instance"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
