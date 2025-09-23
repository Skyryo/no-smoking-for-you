import logging
import os
import uuid
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError, validator

from .services.vertex_ai import (
    get_vertex_ai_service
)
from .services.diagnose_from_text import (
    SmokingAnalysisRequest,
    SmokingAnalysisResponse,
    create_diagnosis_prompt,
    parse_diagnosis_response
)
from .services.diagnose_from_image import (
    ImageAnalysisService,
    create_image_analysis_service
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


class AnalyzeImageResponse(BaseModel):
    """画像分析APIのレスポンスモデル"""
    success: bool = Field(..., description="処理成功フラグ")
    analysis: str = Field(..., description="画像分析結果")


# 画像分析サービスインスタンスを取得
def get_image_analysis_service() -> ImageAnalysisService:
    """画像分析サービスインスタンスを取得"""
    try:
        vertex_ai_service = get_vertex_ai_service()
        return create_image_analysis_service(vertex_ai_service)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"VertexAIサービスの初期化に失敗しました: {str(e)}"
        )


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
        logger.info(f"Received diagnosis request for session: {request.session_id}")
        # VertexAIサービスを取得
        try:
            vertex_ai_service = get_vertex_ai_service()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"VertexAIサービスの初期化に失敗しました: {str(e)}"
            )
        
        # 診断用プロンプトを作成
        prompt = create_diagnosis_prompt(request.questionnaire)
        
        # VertexAI APIを呼び出してテキスト生成
        response_text = await vertex_ai_service.generate_text(prompt)
        
        # レスポンスをパースして診断結果を作成
        analysis_result = parse_diagnosis_response(response_text)
        
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


@app.post("/api/analyze-image", response_model=AnalyzeImageResponse)
async def analyze_image(file: UploadFile = File(...)) -> AnalyzeImageResponse:
    """
    アップロードされた画像から喫煙による健康・肌への影響を分析するエンドポイント
    
    Args:
        file: アップロードされた画像ファイル
    
    Returns:
        画像分析結果
        
    Raises:
        HTTPException: ファイル形式エラー、分析エラー等
    """
    try:
        logger.info(f"Received image analysis request: {file.filename}")
        
        # ファイル形式の検証
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="画像ファイルをアップロードしてください"
            )
        
        # ファイルサイズの検証（10MB制限）
        max_size = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ファイルサイズが大きすぎます（最大10MB）"
            )
        
        # 画像分析サービスを取得
        image_analysis_service = get_image_analysis_service()
        
        # 画像分析を実行
        analysis_result = await image_analysis_service.analyze_image(file_content)
        
        logger.info(f"Image analysis completed successfully for file: {file.filename}")
        
        return AnalyzeImageResponse(
            success=True,
            analysis=analysis_result
        )
        
    except HTTPException:
        # HTTPExceptionは再発生させる
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error during image analysis for file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="画像分析処理中に予期しないエラーが発生しました"
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
        try:
            vertex_ai_service = get_vertex_ai_service()
            vertex_ai_status = vertex_ai_service.health_check()
        except Exception as e:
            vertex_ai_status = {
                "status": "unhealthy",
                "message": f"VertexAIサービスの初期化に失敗しました: {str(e)}"
            }
        
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