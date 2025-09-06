from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from typing import Optional
import magic
from PIL import Image
from io import BytesIO
import logging
from datetime import datetime

from ..core.auth import get_current_user
from ..core.config import settings
from ..services.storage_service import get_storage_service
from ..services.firestore_service import get_firestore_service
from ..models.response_models import SuccessResponse, ErrorResponse
from .websocket import get_websocket_manager

logger = logging.getLogger(__name__)
router = APIRouter()

class UploadException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)

def validate_file_basic(file: UploadFile) -> None:
    """Basic file validation"""
    # Check file size
    if hasattr(file, "size"):
        if file.size > settings.MAX_FILE_SIZE:
            raise UploadException(
                "FILE_TOO_LARGE",
                f"ファイルサイズが大きすぎます（最大: {settings.MAX_FILE_SIZE // (1024*1024)}MB）",
                413
            )
        if file.size < settings.MIN_FILE_SIZE:
            raise UploadException(
                "FILE_TOO_SMALL",
                "ファイルサイズが小さすぎます",
                400
            )
    
    # Check content type
    if file.content_type not in settings.ALLOWED_CONTENT_TYPES:
        raise UploadException(
            "INVALID_FILE_TYPE",
            "JPEG またはPNG形式のファイルを選択してください",
            400
        )

async def validate_file_content(file_content: bytes) -> dict:
    """Validate file content and extract metadata"""
    try:
        # Detect MIME type using libmagic
        detected_type = magic.from_buffer(file_content, mime=True)
        if detected_type not in settings.ALLOWED_CONTENT_TYPES:
            raise UploadException(
                "INVALID_FILE_TYPE",
                f"ファイル内容が不正です。検出タイプ: {detected_type}",
                400
            )
        
        # Validate as image using PIL
        try:
            image = Image.open(BytesIO(file_content))
            width, height = image.size
            image.verify()  # Check image integrity
            
            return {
                "width": width,
                "height": height,
                "format": image.format or "JPEG"
            }
        except Exception:
            raise UploadException(
                "INVALID_FILE_TYPE",
                "画像ファイルが破損している可能性があります",
                400
            )
            
    except UploadException:
        raise
    except Exception as e:
        logger.error(f"File content validation error: {e}")
        raise UploadException(
            "INVALID_FILE_TYPE",
            "ファイルの検証に失敗しました",
            400
        )

def create_error_response(error: UploadException) -> JSONResponse:
    """Create standardized error response"""
    return JSONResponse(
        status_code=error.status_code,
        content={
            "success": False,
            "error": {
                "code": error.code,
                "message": error.message
            }
        }
    )

@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    user: dict = Depends(get_current_user)
):
    """
    Upload image file to Cloud Storage and save metadata to Firestore
    
    - **file**: Image file (JPEG/PNG, max 10MB)
    - **session_id**: Optional session ID
    """
    try:
        # Get WebSocket manager for progress updates
        ws_manager = get_websocket_manager()
        
        # Basic file validation
        validate_file_basic(file)
        
        # Send progress update: validation started
        if session_id:
            await ws_manager.send_progress_update(session_id, "validating", 10, "ファイル検証中...")
        
        # Read file content
        file_content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Content validation and metadata extraction
        image_dimensions = await validate_file_content(file_content)
        
        # Send progress update: validation complete
        if session_id:
            await ws_manager.send_progress_update(session_id, "uploading", 30, "アップロード中...")
        
        # Generate IDs
        firestore_service = get_firestore_service()
        storage_service = get_storage_service()
        
        image_id = firestore_service.generate_image_id()
        if not session_id:
            session_id = firestore_service.generate_session_id()
            # Create session document
            await firestore_service.create_session_document(session_id, user["uid"])
        
        # Update session status to uploading
        await firestore_service.update_session_status(session_id, "uploading")
        
        # Send progress update: storing file
        await ws_manager.send_progress_update(session_id, "storing", 60, "ファイル保存中...")
        
        # Upload to Cloud Storage
        original_url = await storage_service.upload_image(
            file_content=file_content,
            filename=file.filename,
            session_id=session_id,
            content_type=file.content_type
        )
        
        # Send progress update: saving metadata
        await ws_manager.send_progress_update(session_id, "saving", 80, "メタデータ保存中...")
        
        # Prepare metadata
        metadata = {
            "filename": file.filename,
            "contentType": file.content_type,
            "size": len(file_content),
            "dimensions": image_dimensions
        }
        
        # Save to Firestore
        await firestore_service.create_image_document(
            image_id=image_id,
            session_id=session_id,
            user_id=user["uid"],
            original_url=original_url,
            metadata=metadata
        )
        
        # Update session status to completed
        await firestore_service.update_session_status(
            session_id, "image_uploaded", image_id
        )
        
        # Send final progress update
        await ws_manager.send_progress_update(session_id, "completed", 100, "アップロード完了")
        
        # Return success response
        return {
            "success": True,
            "data": {
                "imageId": image_id,
                "sessionId": session_id,
                "uploadedAt": datetime.utcnow().isoformat(),
                "originalUrl": original_url,
                "metadata": metadata
            }
        }
        
    except UploadException as e:
        # Send WebSocket error notification
        ws_manager = get_websocket_manager()
        if session_id:
            await ws_manager.send_error(session_id, e.code, e.message)
        
        await firestore_service.update_session_status(session_id or "unknown", "failed")
        return create_error_response(e)
    except Exception as e:
        logger.error(f"Unexpected upload error: {e}")
        
        # Send WebSocket error notification
        ws_manager = get_websocket_manager()
        if session_id:
            await ws_manager.send_error(session_id, "INTERNAL_ERROR", "予期しないエラーが発生しました")
        
        await firestore_service.update_session_status(session_id or "unknown", "failed")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "予期しないエラーが発生しました"
                }
            }
        )

@router.get("/upload-status/{session_id}")
async def get_upload_status(
    session_id: str,
    user: dict = Depends(get_current_user)
):
    """Get upload status for a session"""
    try:
        # TODO: Add proper session ownership validation
        return {
            "success": True,
            "data": {
                "sessionId": session_id,
                "status": "completed"  # Placeholder
            }
        }
    except Exception as e:
        logger.error(f"Error getting upload status: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "ステータスの取得に失敗しました"
                }
            }
        )
