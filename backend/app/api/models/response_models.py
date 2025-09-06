from pydantic import BaseModel
from typing import Optional, Any

class SuccessResponse(BaseModel):
    success: bool = True
    data: Any

class ErrorResponse(BaseModel):
    success: bool = False
    error: dict

class ImageUploadSuccessResponse(SuccessResponse):
    data: dict  # Contains imageId, sessionId, originalUrl, metadata

class ProgressUpdate(BaseModel):
    type: str = "upload_progress"
    data: dict

class ErrorUpdate(BaseModel):
    type: str = "upload_error"
    data: dict
