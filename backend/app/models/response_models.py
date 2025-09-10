from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from .request_models import SmokingStatus, CigaretteType, QuitIntention, SmokingPatternItem

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

# 喫煙習慣レスポンス関連
class ErrorDetail(BaseModel):
    field: str
    message: str

class SmokingHabitsData(BaseModel):
    smoking_status: SmokingStatus
    daily_cigarettes: Optional[int] = None
    smoking_years: Optional[int] = None
    quit_date: Optional[str] = None
    cigarette_type: Optional[CigaretteType] = None
    tar_content: Optional[float] = None
    nicotine_content: Optional[float] = None
    quit_intention: Optional[QuitIntention] = None
    smoking_pattern: Optional[List[SmokingPatternItem]] = None

class SmokingHabitsResponseData(BaseModel):
    questionnaire_id: str
    session_id: str
    submitted_at: str
    smoking_habits: SmokingHabitsData

class SmokingHabitsResponse(SuccessResponse):
    data: SmokingHabitsResponseData
