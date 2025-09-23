import base64
import logging
from fastapi import UploadFile
from io import BytesIO
from google.genai import types
from google import genai
from PIL import Image

from pip._vendor.pygments.unistring import No


logger = logging.getLogger(__name__)


def generate_image_from_prompt(prompt: str, upload_file: UploadFile) -> str:
    """
    Vertex AI の Gemini 2.5 Flash Image Preview モデルを使用して画像を生成する
    
    Args:
        prompt (str): 画像生成のためのプロンプトテキスト
        image (Optional[PIL.Image]): 参考画像（オプション）
    
    Returns:
        str: 生成された画像のbase64エンコードされた文字列
    
    Raises:
        Exception: 画像生成中にエラーが発生した場合
    """
    try:
        # Vertex AI クライアントの設定
        client = genai.Client(
            vertexai=True,
            project="no-smoking-adk-app",
            location="global"
        )
         
        logger.info(f"画像生成を開始します。プロンプト: {prompt}")
        image = Image.open(upload_file.file)

        # 画像生成の実行
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[f"generate 20 years laters smoking effects appearance. his/her smoking habit is here: {prompt}", image],
            config=types.GenerateContentConfig(
              response_modalities=[
                types.Modality.TEXT,
                types.Modality.IMAGE,
              ],
            )
        )
        logger.info("画像生成が完了しました。")
                
        # レスポンスの存在確認
        if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
            raise Exception("画像生成のレスポンスが空です")
        # レスポンスから画像データを抽出
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None and part.inline_data.mime_type == 'image/png':
                try:
                    decoded_data = base64.b64decode(part.inline_data.data)       
                    generated_image = Image.open(BytesIO(decoded_data))
                   
                    # Pillowで再度base64エンコードして返す
                    buffer = BytesIO()
                    generated_image.save(buffer, format='PNG')
                        
                    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

                    return image_base64

                except Exception as e:
                    logger.error(f"画像データの処理中にエラーが発生しました: {e}")
                    # デコードに失敗した場合は、元のデータをそのままbase64エンコードして返す
                    logger.warning("base64デコードに失敗したため、生のデータをエンコードして返します。")
                    return base64.b64encode(part.inline_data.data).decode('utf-8')

        # 画像データが見つからない場合
        raise Exception("生成された画像データが見つかりませんでした")
        
    except Exception as e:
        logger.error(f"画像生成中にエラーが発生しました: {str(e)}")
        raise Exception(f"画像生成に失敗しました: {str(e)}")