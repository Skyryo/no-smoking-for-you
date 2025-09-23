"""
テキスト問診データからの診断用プロンプト・型定義専用モジュール
"""
import json
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, validator

# ロガーの設定
logger = logging.getLogger(__name__)


class Gender(str, Enum):
    """性別の選択肢"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class CigaretteType(str, Enum):
    """タバコの種類"""
    REGULAR = "通常タバコ"
    MENTHOL = "メンソールタバコ"
    ELECTRONIC = "電子タバコ"


class SmokingAnalysisRequest(BaseModel):
    """問診データのリクエストモデル"""
    current_age: int = Field(..., ge=1, le=120, description="現在の年齢")
    gender: Gender = Field(..., description="性別")
    smoking_start_age: int = Field(..., ge=1, le=120, description="喫煙開始年齢")
    daily_cigarettes: int = Field(..., ge=0, le=100, description="1日あたり喫煙本数")
    cigarette_type: CigaretteType = Field(..., description="タバコの種類")
    cigarette_brand: Optional[str] = Field(None, max_length=32, description="ブランド名")
    quit_attempts: int = Field(..., ge=0, le=99, description="禁煙試行回数")
    current_health_issues: Optional[List[str]] = Field(
        None, max_items=8, description="現在の健康問題"
    )
    exercise_frequency: int = Field(..., ge=0, le=7, description="運動頻度（週回数）")
    alcohol_consumption: int = Field(..., ge=0, le=7, description="飲酒頻度（週回数）")
    sleep_hours: float = Field(..., ge=0, le=24, description="睡眠時間")
    previous_medical_advice: Optional[str] = Field(
        None, max_length=128, description="過去の医師からの助言"
    )

    @validator('smoking_start_age')
    def validate_smoking_start_age(cls, v, values):
        if 'current_age' in values and v > values['current_age']:
            raise ValueError('喫煙開始年齢は現在の年齢以下である必要があります')
        return v


class SmokingHabitsResults(BaseModel):
    """喫煙習慣の分析結果"""
    smoking_duration_years: int
    pack_years: float
    addiction_level: str
    health_risk_score: int
    quit_success_probability: float


class CurrentEffectsResults(BaseModel):
    """現在の影響分析結果"""
    respiratory_impact: str
    cardiovascular_impact: str
    skin_condition_assessment: str
    overall_health_status: str


class SmokingAnalysisResponse(BaseModel):
    """分析結果のレスポンスモデル"""
    current_skin_status: str
    predicted_impact: str
    smoking_habits_results: SmokingHabitsResults
    current_effects_results: CurrentEffectsResults


def create_diagnosis_prompt(data: SmokingAnalysisRequest) -> str:
    """
    診断用のプロンプトを作成
    
    Args:
        data: 問診データ
        
    Returns:
        診断用プロンプト文字列
    """
    health_issues_text = "なし"
    if data.current_health_issues:
        health_issues_text = "、".join(data.current_health_issues)
    
    medical_advice_text = "なし"
    if data.previous_medical_advice:
        medical_advice_text = data.previous_medical_advice

    prompt = f"""
あなたは経験豊富な医師として、以下の喫煙者の問診データを分析し、肌の状態と健康への影響を評価してください。

## 患者データ
- 年齢: {data.current_age}歳
- 性別: {data.gender.value}
- 喫煙開始年齢: {data.smoking_start_age}歳
- 1日の喫煙本数: {data.daily_cigarettes}本
- タバコの種類: {data.cigarette_type.value}
- ブランド: {data.cigarette_brand or "不明"}
- 禁煙試行回数: {data.quit_attempts}回
- 現在の健康問題: {health_issues_text}
- 運動頻度: 週{data.exercise_frequency}回
- 飲酒頻度: 週{data.alcohol_consumption}回
- 睡眠時間: {data.sleep_hours}時間
- 過去の医師からの助言: {medical_advice_text}

## 回答形式
以下のJSON形式で回答してください：

{{
    "current_skin_status": "現在の肌の状態の詳細な評価（200文字程度）",
    "predicted_impact": "今後予想される健康への影響（200文字程度）",
    "smoking_habits_results": {{
        "smoking_duration_years": 喫煙年数（整数）,
        "pack_years": パック・イヤー（浮動小数点）,
        "addiction_level": "依存度レベル（軽度/中等度/重度）",
        "health_risk_score": "健康リスクスコア（1-100の整数）",
        "quit_success_probability": "禁煙成功確率（0-1の浮動小数点）"
    }},
    "current_effects_results": {{
        "respiratory_impact": "呼吸器への影響（100文字程度）",
        "cardiovascular_impact": "心血管系への影響（100文字程度）",
        "skin_condition_assessment": "肌状態の評価（100文字程度）",
        "overall_health_status": "総合的な健康状態（100文字程度）"
    }}
}}

## 注意事項
- 医学的根拠に基づいた分析を行ってください
- 肌への影響を特に重視してください
- パック・イヤー = (1日の喫煙本数 ÷ 20) × 喫煙年数で計算してください
- 禁煙成功確率は過去の試行回数と現在の状況を考慮してください
- 健康リスクスコアは総合的な健康リスクを1-100で評価してください
"""
    return prompt


def parse_diagnosis_response(response_text: str) -> SmokingAnalysisResponse:
    """
    AIからのレスポンスをパースして診断結果として返す
    
    Args:
        response_text: AIからのレスポンステキスト
        
    Returns:
        パースされた診断結果
        
    Raises:
        Exception: パースエラー
    """
    try:
        # JSONの開始と終了を見つける
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            raise ValueError("JSONフォーマットが見つかりません")
            
        json_text = response_text[start_idx:end_idx + 1]
        
        # JSONをパース
        response_data = json.loads(json_text)
        
        # Pydanticモデルに変換
        smoking_habits = SmokingHabitsResults(**response_data["smoking_habits_results"])
        current_effects = CurrentEffectsResults(**response_data["current_effects_results"])
        
        result = SmokingAnalysisResponse(
            current_skin_status=response_data["current_skin_status"],
            predicted_impact=response_data["predicted_impact"],
            smoking_habits_results=smoking_habits,
            current_effects_results=current_effects
        )
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {str(e)}")
        raise Exception(f"レスポンスの解析に失敗しました: {str(e)}")
    except KeyError as e:
        logger.error(f"Missing required field: {str(e)}")
        raise Exception(f"必要なフィールドが不足しています: {str(e)}")
    except Exception as e:
        logger.error(f"Response parsing error: {str(e)}")
        raise Exception(f"レスポンス処理中にエラーが発生しました: {str(e)}")


def calculate_smoking_statistics(data: SmokingAnalysisRequest) -> Dict[str, Any]:
    """
    問診データから基本的な喫煙統計を計算
    
    Args:
        data: 問診データ
        
    Returns:
        喫煙統計情報
    """
    smoking_duration = data.current_age - data.smoking_start_age
    pack_years = (data.daily_cigarettes / 20) * smoking_duration
    
    return {
        "smoking_duration_years": smoking_duration,
        "pack_years": round(pack_years, 2),
        "daily_cigarettes": data.daily_cigarettes,
        "cigarette_type": data.cigarette_type.value
    }