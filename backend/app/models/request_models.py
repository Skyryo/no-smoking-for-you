from pydantic import BaseModel
from typing import Optional

class UploadImageRequest(BaseModel):
    session_id: Optional[str] = None

class FileMetadata(BaseModel):
    filename: str
    content_type: str
    size: int
    dimensions: dict

class UploadImageResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    
class UploadImageData(BaseModel):
    image_id: str
    session_id: str
    uploaded_at: str
    original_url: str
    metadata: FileMetadata

class UploadImageError(BaseModel):
    success: bool = False
    error: dict
