import logging
import os
import uuid
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, status, File, UploadFile, Form
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
from .services.generate_image import (
    generate_image_from_prompt
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


class GenerateImageResponse(BaseModel):
    """画像生成APIのレスポンスモデル"""
    success: bool = Field(..., description="処理成功フラグ")
    image_base64: str = Field(..., description="生成された画像のbase64データ")


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
        
        # 画像分析サービスを取得
        image_analysis_service = get_image_analysis_service()
        
        # 画像分析を実行（UploadFileを直接渡す）
        analysis_result = await image_analysis_service.analyze_image_from_upload(file)
        
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


@app.post("/api/generate-image", response_model=GenerateImageResponse)
async def generate_image(
    prompt: str = Form(..., description="画像生成用のプロンプトテキスト"),
    file: UploadFile = File(..., description="参考画像（必須）")
) -> GenerateImageResponse:
    """
    プロンプトテキストと参考画像から画像を生成するエンドポイント
    
    Args:
        prompt: 画像生成用のプロンプトテキスト（必須）
        image: 参考画像ファイル（必須）
    
    Returns:
        生成された画像のbase64データ
        
    Raises:
        HTTPException: バリデーションエラー、生成エラー等
    """
    try:
        logger.info(f"画像生成リクエストを受信: プロンプト='{prompt}', 画像ファイル={file.filename if file else 'なし'}")

        # ファイル形式の検証
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="画像ファイルをアップロードしてください"
            )
        
        if not prompt or not prompt.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="プロンプトテキストは必須です"
            )
        
        # 画像生成の実行
        try:
            generated_image_base64 = generate_image_from_prompt(prompt.strip(), file)
        except Exception as e:
            logger.error(f"画像生成中にエラーが発生: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"画像生成に失敗しました: {str(e)}"
            )
        
        logger.info("画像生成が正常に完了しました")
        
        return GenerateImageResponse(
            success=True,
            image_base64=generated_image_base64
        )
        
    except HTTPException:
        # HTTPExceptionは再発生させる
        raise
        
    except Exception as e:
        logger.error(f"画像生成処理中に予期しないエラーが発生: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="画像生成処理中に予期しないエラーが発生しました"
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