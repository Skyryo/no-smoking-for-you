"""
画像から喫煙による健康・肌への影響を分析するサービス
"""
import logging
from PIL import Image
from fastapi import UploadFile
from .vertex_ai import VertexAIService

# ロガーの設定
logger = logging.getLogger(__name__)

class ImageAnalysisService:
    """画像分析サービスクラス"""
    
    def __init__(self, vertex_ai_service: VertexAIService):
        """
        画像分析サービスを初期化
        
        Args:
            vertex_ai_service: VertexAIサービスインスタンス
        """
        self.vertex_ai_service = vertex_ai_service
        logger.info("ImageAnalysisService initialized")

    async def analyze_image_from_upload(
        self,
        file: UploadFile,
        analysis_type: str = "smoking_effects"
    ) -> str:
        """
        UploadFileから直接画像を分析して喫煙による影響を診断
        
        Args:
            file: アップロードされた画像ファイル
            analysis_type: 分析タイプ（現在は'smoking_effects'のみ）
            
        Returns:
            分析結果の文字列
            
        Raises:
            Exception: 画像分析エラー
        """
        try:
            logger.info(f"Starting image analysis with type: {analysis_type}")
            
            # 画像を検証（ファイルサイズとPIL読み込み可能性）
            pil_image = self._validate_and_load_image_from_upload(file)
            
            # 分析用プロンプトを作成
            prompt = self._create_analysis_prompt(analysis_type)
            
            # VertexAIサービスの画像分析機能を使用
            analysis_result = await self.vertex_ai_service.analyze_image_with_pil(
                pil_image=pil_image,
                prompt=prompt
            )
                
            logger.info("Image analysis completed successfully")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            raise Exception(f"画像分析に失敗しました: {str(e)}")

  

    def _validate_and_load_image_from_upload(self, file: UploadFile) -> Image.Image:
        """
        UploadFileから画像を検証・読み込み
        
        Args:
            file: アップロードされた画像ファイル
            
        Returns:
            PIL.Image: 読み込まれた画像
            
        Raises:
            Exception: 画像データが不正な場合
        """
        try:
            # ファイルサイズの検証（10MB制限）
            max_size = 10 * 1024 * 1024  # 10MB
            file.file.seek(0, 2)  # ファイル末尾に移動
            file_size = file.file.tell()
            file.file.seek(0)  # ファイル先頭に戻る
            
            if file_size > max_size:
                raise Exception("ファイルサイズが大きすぎます（最大10MB）")
            
            # PILで画像を直接開いて検証
            image = Image.open(file.file)
            
            # 基本的な検証
            if image.size[0] < 50 or image.size[1] < 50:
                raise Exception("画像サイズが小さすぎます（最小50x50ピクセル）")
            
            if image.size[0] > 4096 or image.size[1] > 4096:
                raise Exception("画像サイズが大きすぎます（最大4096x4096ピクセル）")
            
            # サポートされている形式かチェック
            if image.format not in ['JPEG', 'PNG', 'WebP']:
                raise Exception(f"サポートされていない画像形式です: {image.format}")
                
            logger.info(f"Image validation passed: {image.format}, {image.size}")
            
            # ファイルポインタを先頭に戻す
            file.file.seek(0)
            
            return image
            
        except Exception as e:
            if "画像" in str(e):
                raise  # 既に適切なエラーメッセージ
            else:
                raise Exception(f"画像データが不正です: {str(e)}")

    def _create_analysis_prompt(self, analysis_type: str) -> str:
        """
        分析用プロンプトを作成
        
        Args:
            analysis_type: 分析タイプ
            
        Returns:
            分析用プロンプト文字列
        """
        if analysis_type == "smoking_effects":
            return """
この画像を分析して、喫煙による健康や肌への影響の兆候を詳しく調べてください。

分析してください：
1. 肌の状態（しわ、くすみ、色素沈着、弾力性など）
2. 歯や歯茎の状態（黄ばみ、歯茎の色など）
3. 目の周りの状態（クマ、小じわなど）
4. 全体的な健康的な印象

可能な限り具体的で建設的なアドバイスを含めて、分析結果を日本語で返してください。
ただし、医学的診断ではなく、一般的な健康・美容に関する観察結果として提示してください。

画像に人物が写っていない場合や分析できない場合は、その旨を説明してください。
"""
        else:
            return f"画像を分析してください。分析タイプ: {analysis_type}"


def create_image_analysis_service(vertex_ai_service: VertexAIService) -> ImageAnalysisService:
    """
    画像分析サービスインスタンスを作成
    
    Args:
        vertex_ai_service: VertexAIサービスインスタンス
        
    Returns:
        ImageAnalysisServiceインスタンス
    """
    return ImageAnalysisService(vertex_ai_service)