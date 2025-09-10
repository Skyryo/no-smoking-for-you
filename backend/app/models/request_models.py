from pydantic import BaseModel, validator, Field
from typing import Optional, List, Literal
from enum import Enum

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

# 喫煙習慣関連のモデル
class SmokingStatus(str, Enum):
    SMOKER = "smoker"
    NON_SMOKER = "non_smoker"
    EX_SMOKER = "ex_smoker"

class CigaretteType(str, Enum):
    TRADITIONAL = "traditional"
    ELECTRONIC = "electronic"
    BOTH = "both"

class QuitIntention(str, Enum):
    PLANNING = "planning"
    CONSIDERING = "considering"
    NOT_INTERESTED = "not_interested"

class SmokingPatternItem(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"

class SmokingHabitsRequest(BaseModel):
    session_id: Optional[str] = None
    smoking_status: SmokingStatus
    daily_cigarettes: Optional[int] = Field(None, ge=1, le=100)
    smoking_years: Optional[int] = Field(None, ge=1, le=80)
    quit_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}$')
    cigarette_type: Optional[CigaretteType] = None
    tar_content: Optional[float] = Field(None, ge=1, le=25)
    nicotine_content: Optional[float] = Field(None, ge=0.1, le=3.0)
    quit_intention: Optional[QuitIntention] = None
    smoking_pattern: Optional[List[SmokingPatternItem]] = None

    @validator('daily_cigarettes')
    def validate_daily_cigarettes(cls, v, values):
        if values.get('smoking_status') == SmokingStatus.SMOKER and v is None:
            raise ValueError('喫煙者の場合、1日の喫煙本数は必須です')
        if v is not None and (v < 1 or v > 100):
            raise ValueError('1日の喫煙本数は1-100本で入力してください')
        return v

    @validator('smoking_years')
    def validate_smoking_years(cls, v, values):
        smoking_status = values.get('smoking_status')
        if smoking_status in [SmokingStatus.SMOKER, SmokingStatus.EX_SMOKER] and v is None:
            raise ValueError('喫煙者または元喫煙者の場合、喫煙年数は必須です')
        if v is not None and (v < 1 or v > 80):
            raise ValueError('喫煙年数は1-80年で入力してください')
        return v

    @validator('quit_date')
    def validate_quit_date(cls, v, values):
        if values.get('smoking_status') == SmokingStatus.EX_SMOKER and v is None:
            raise ValueError('元喫煙者の場合、禁煙開始時期は必須です')
        if v is not None:
            from datetime import datetime
            try:
                quit_datetime = datetime.strptime(v, '%Y-%m')
                if quit_datetime > datetime.now():
                    raise ValueError('禁煙日は現在より未来の日付にできません')
            except ValueError as e:
                if 'does not match format' in str(e):
                    raise ValueError('禁煙日はYYYY-MM形式で入力してください')
                raise e
        return v

    @validator('cigarette_type')
    def validate_cigarette_type(cls, v, values):
        if values.get('smoking_status') == SmokingStatus.SMOKER and v is None:
            raise ValueError('喫煙者の場合、タバコの種類は必須です')
        return v
