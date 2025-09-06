import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class FirebaseAuth:
    def __init__(self, credentials_path: Optional[str] = None):
        """Initialize Firebase Admin SDK"""
        try:
            if not firebase_admin._apps:
                if credentials_path:
                    cred = credentials.Certificate(credentials_path)
                    firebase_admin.initialize_app(cred)
                else:
                    # Use default credentials in Cloud environments
                    firebase_admin.initialize_app()
            logger.info("Firebase Admin SDK initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise

    async def verify_token(self, token: str) -> dict:
        """Verify Firebase ID token and return decoded claims"""
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=401,
                detail={
                    "success": False,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "認証が必要です"
                    }
                }
            )

# Global Firebase instance
firebase_auth = FirebaseAuth()
security = HTTPBearer()

async def verify_firebase_token(token: str = Depends(security)) -> dict:
    """FastAPI dependency for Firebase token verification"""
    return await firebase_auth.verify_token(token.credentials)

async def get_current_user(token_data: dict = Depends(verify_firebase_token)) -> dict:
    """Get current authenticated user information"""
    return {
        "uid": token_data["uid"],
        "email": token_data.get("email"),
        "name": token_data.get("name"),
        "picture": token_data.get("picture")
    }
