import logging
import os
import uuid
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError, validator

from .services.vertex_ai import (
    SmokingAnalysisRequest, 
    SmokingAnalysisResponse, 
    VertexAIService,
    create_vertex_ai_service
)

# ロガーの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="No Smoking ADK API", version="1.0.0")

# CORS設定 - フロントエンドからのアクセスを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では具体的なオリジンを指定することを推奨
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """ルートエンドポイント - ヘルスチェック用"""
    return {"status": "healthy"}

@app.get("/hello")
async def hello():
    """Hello Worldメッセージを返すエンドポイント"""
    return {"message": "Hello World"}


# リクエスト/レスポンスモデル
class DiagnoseRequest(BaseModel):
    """診断APIのリクエストモデル"""
    session_id: str = Field(..., description="セッションID（UUID形式）")
    questionnaire: SmokingAnalysisRequest = Field(..., description="問診データ")

    @validator('session_id')
    def validate_session_id(cls, v):
        """セッションIDがUUID形式かチェック"""
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("session_idはUUID形式である必要があります")


class DiagnoseResponse(BaseModel):
    """診断APIのレスポンスモデル"""
    success: bool = Field(..., description="処理成功フラグ")
    data: SmokingAnalysisResponse = Field(..., description="診断結果データ")


class ErrorResponse(BaseModel):
    """エラーレスポンスモデル"""
    success: bool = Field(False, description="処理成功フラグ")
    error: str = Field(..., description="エラーメッセージ")
    detail: str = Field(None, description="詳細エラー情報")


# VertexAIサービスインスタンスを取得
def get_vertex_ai_service() -> VertexAIService:
    """VertexAIサービスインスタンスを取得"""
    # project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    project_id = "no-smoking-adk-app"
    if not project_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google Cloud Project IDが設定されていません"
        )
    return create_vertex_ai_service(project_id)


@app.post("/api/diagnose", response_model=DiagnoseResponse)
async def diagnose(request: DiagnoseRequest) -> DiagnoseResponse:
    """
    問診データに基づいて喫煙による健康・肌への影響を診断するエンドポイント
    
    Args:
        request: 診断リクエスト（セッションIDと問診データを含む）
    
    Returns:
        診断結果
        
    Raises:
        HTTPException: バリデーションエラー、サーバーエラー等
    """
    try:
        # セッションIDのバリデーション
        try:
            uuid.UUID(request.session_id)
        except ValueError:
            logger.warning(f"Invalid session_id format: {request.session_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="session_idはUUID形式である必要があります"
            )
        
        logger.info(f"Starting diagnosis for session: {request.session_id}")
        
        # VertexAIサービスを取得
        vertex_ai_service = get_vertex_ai_service()
        
        # 問診データの分析を実行
        analysis_result = await vertex_ai_service.analyze_smoking_data(request.questionnaire)
        
        logger.info(f"Diagnosis completed successfully for session: {request.session_id}")
        
        return DiagnoseResponse(
            success=True,
            data=analysis_result
        )
        
    except ValidationError as e:
        logger.error(f"Validation error for session {request.session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"リクエストデータが不正です: {str(e)}"
        )
        
    except HTTPException:
        # HTTPExceptionは再発生させる
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error during diagnosis for session {request.session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="診断処理中に予期しないエラーが発生しました"
        )


@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """
    APIとVertexAIサービスのヘルスチェック
    
    Returns:
        サービス状態情報
    """
    try:
        # VertexAIサービスのヘルスチェック
        vertex_ai_service = get_vertex_ai_service()
        vertex_ai_status = vertex_ai_service.health_check()
        
        return {
            "status": "healthy",
            "api_version": "1.0.0",
            "vertex_ai": vertex_ai_status,
            "message": "All services are running normally"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"サービスが利用できません: {str(e)}"
        )