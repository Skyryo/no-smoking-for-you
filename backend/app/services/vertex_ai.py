"""
VertexAI gemini-2.5-flashとのやりとりを行う汎用的なサービス
"""
import logging
import os
from typing import Dict, Any, Optional
from io import BytesIO
from PIL import Image
from google import genai

# ロガーの設定
logger = logging.getLogger(__name__)


class VertexAIService:
    """VertexAI gemini-2.5-flash汎用サービスクラス"""
    
    def __init__(self, project_id: str, location: str = "us-central1", model_name: str = "gemini-2.5-flash"):
        """
        VertexAIサービスを初期化
        
        Args:
            project_id: Google Cloud Project ID
            location: VertexAIのロケーション
            model_name: 使用するモデル名
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        
        # Google Gen AI SDKクライアントを初期化（VertexAI用）
        try:
            self.client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location
            )
            logger.info(f"VertexAI initialized with project: {self.project_id}, location: {self.location}, model: {self.model_name}")
        except Exception as e:
            logger.error(f"VertexAI initialization failed: {str(e)}")
            raise

    async def generate_text(
        self,
        prompt: str,
        model_name: Optional[str] = None
    ) -> str:
        """
        テキスト生成を実行
        
        Args:
            prompt: 生成用プロンプト
            model_name: 使用するモデル名（省略時はデフォルト）
            
        Returns:
            生成されたテキスト
            
        Raises:
            Exception: VertexAI API呼び出しエラー
        """
        try:
            logger.info(f"VertexAI text generation starting... project={self.project_id}, location={self.location}")
            
            # モデル名の決定
            used_model = model_name or self.model_name
            
            # API呼び出し（Google Gen AI SDK使用）
            response = self.client.models.generate_content(
                model=used_model,
                contents=prompt
            )
            
            if not response.text:
                raise Exception("VertexAIから空のレスポンスが返されました")
                
            logger.info("VertexAI text generation completed successfully")
            return response.text
            
        except Exception as e:
            logger.error(f"VertexAI text generation failed: {str(e)}")
            raise Exception(f"VertexAI テキスト生成に失敗しました: {str(e)}")


    async def analyze_image_with_pil(
        self,
        pil_image: Image.Image,
        prompt: str,
        model_name: Optional[str] = None
    ) -> str:
        """
        PIL.Imageとテキストプロンプトを組み合わせて分析を実行（効率化版）
        
        Args:
            pil_image: PIL.Image オブジェクト
            prompt: 分析用プロンプト
            model_name: 使用するモデル名（省略時はデフォルト）
            
        Returns:
            分析結果テキスト
            
        Raises:
            Exception: VertexAI API呼び出しエラー
        """
        try:
            logger.info(f"VertexAI image analysis starting... project={self.project_id}, location={self.location}")
            
            # モデル名の決定
            used_model = model_name or self.model_name
            
            response = self.client.models.generate_content(
                model=used_model,
                contents=[prompt, pil_image]
            )
            
            if not response.text:
                raise Exception("VertexAIから空のレスポンスが返されました")
                
            logger.info("VertexAI image analysis completed successfully")
            return response.text
            
        except Exception as e:
            logger.error(f"VertexAI image analysis failed: {str(e)}")
            raise Exception(f"VertexAI 画像分析に失敗しました: {str(e)}")


    def health_check(self) -> Dict[str, Any]:
        """
        VertexAIサービスのヘルスチェック
        
        Returns:
            サービス状態情報
        """
        try:
            # クライアントの初期化確認
            if self.client is None:
                return {
                    "status": "unhealthy",
                    "message": "VertexAI client not initialized",
                    "project_id": self.project_id,
                    "location": self.location
                }
            
            return {
                "status": "healthy",
                "message": "VertexAI service is ready",
                "project_id": self.project_id,
                "location": self.location,
                "model": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"VertexAI service error: {str(e)}",
                "project_id": self.project_id,
                "location": self.location
            }

# サービスインスタンスを作成（実際の使用時にproject_idを設定）
def create_vertex_ai_service(
    project_id: str,
    location: str = "us-central1",
    model_name: str = "gemini-2.5-flash"
) -> VertexAIService:
    """
    VertexAIサービスインスタンスを作成
    
    Args:
        project_id: Google Cloud Project ID
        location: VertexAIのロケーション
        model_name: 使用するモデル名
        
    Returns:
        VertexAIServiceインスタンス
    """
    return VertexAIService(project_id=project_id, location=location, model_name=model_name)


def get_vertex_ai_service(model_name: str = "gemini-2.5-flash") -> VertexAIService:
    """
    VertexAIサービスインスタンスを取得
    
    Args:
        model_name: 使用するモデル名（デフォルト: gemini-2.5-flash）
        
    Returns:
        VertexAIServiceインスタンス
        
    Raises:
        Exception: Google Cloud Project IDが設定されていない場合
    """
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "no-smoking-adk-app")
    if not project_id:
        raise Exception("Google Cloud Project IDが設定されていません")
    
    return create_vertex_ai_service(project_id, model_name=model_name)