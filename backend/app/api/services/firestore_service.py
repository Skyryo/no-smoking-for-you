from google.cloud import firestore
from google.cloud.firestore_v1 import FieldFilter
from datetime import datetime
import uuid
import logging
from typing import Optional, Dict, Any
from ..core.config import settings

logger = logging.getLogger(__name__)

class FirestoreService:
    def __init__(self):
        """Initialize Firestore client"""
        try:
            self.db = firestore.Client(project=settings.GCP_PROJECT_ID)
            logger.info("Firestore service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore: {e}")
            raise

    async def create_image_document(self, 
                                   image_id: str,
                                   session_id: str, 
                                   user_id: str,
                                   original_url: str,
                                   metadata: dict) -> str:
        """Create image document in Firestore"""
        try:
            doc_ref = self.db.collection("images").document(image_id)
            
            image_data = {
                "imageId": image_id,
                "sessionId": session_id,
                "userId": user_id,
                "originalUrl": original_url,
                "metadata": metadata,
                "uploadedAt": firestore.SERVER_TIMESTAMP,
                "createdAt": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP
            }
            
            doc_ref.set(image_data)
            logger.info(f"Image document created: {image_id}")
            return image_id
            
        except Exception as e:
            logger.error(f"Failed to create image document: {e}")
            raise Exception("データの保存に失敗しました")

    async def update_session_status(self, session_id: str, status: str, image_id: Optional[str] = None) -> None:
        """Update session status in Firestore"""
        try:
            doc_ref = self.db.collection("sessions").document(session_id)
            
            update_data = {
                "status": status,
                "updatedAt": firestore.SERVER_TIMESTAMP
            }
            
            if image_id:
                update_data["imageId"] = image_id
            
            doc_ref.set(update_data, merge=True)
            logger.info(f"Session status updated: {session_id} -> {status}")
            
        except Exception as e:
            logger.error(f"Failed to update session status: {e}")
            # Do not raise exception for session updates as they are not critical

    async def get_image_document(self, image_id: str) -> Optional[Dict[str, Any]]:
        """Get image document from Firestore"""
        try:
            doc_ref = self.db.collection("images").document(image_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get image document {image_id}: {e}")
            return None

    async def create_session_document(self, session_id: str, user_id: str) -> str:
        """Create session document in Firestore"""
        try:
            doc_ref = self.db.collection("sessions").document(session_id)
            
            session_data = {
                "sessionId": session_id,
                "userId": user_id,
                "status": "uploading",
                "createdAt": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP
            }
            
            doc_ref.set(session_data)
            logger.info(f"Session document created: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session document: {e}")
            raise Exception("セッションの作成に失敗しました")

    def generate_image_id(self) -> str:
        """Generate unique image ID"""
        return str(uuid.uuid4())

    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        return str(uuid.uuid4())

# Global firestore service instance - initialized on demand
_firestore_service = None

def get_firestore_service() -> FirestoreService:
    """Get or create firestore service instance"""
    global _firestore_service
    if _firestore_service is None:
        _firestore_service = FirestoreService()
    return _firestore_service
