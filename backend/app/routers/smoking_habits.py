from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid
from typing import Dict, Any

from ..models.request_models import SmokingHabitsRequest
from ..models.response_models import SmokingHabitsResponse, SmokingHabitsResponseData, SmokingHabitsData

router = APIRouter()

@router.post("/smoking-habits", response_model=SmokingHabitsResponse)
async def submit_smoking_habits(
    smoking_habits: SmokingHabitsRequest,
) -> SmokingHabitsResponse:
    """
    喫煙習慣に関する問診データを保存する
    
    Args:
        smoking_habits: 喫煙習慣データ
        
    Returns:
        SmokingHabitsResponse: 保存結果
        
    Raises:
        HTTPException: バリデーションエラーまたはサーバーエラー
    """
    try:
        # Pydanticのバリデーションは自動で行われる
        # 追加のビジネスロジックバリデーション
        validation_errors = []
        
        # 喫煙者の必須項目チェック
        if smoking_habits.smoking_status == "smoker":
            if smoking_habits.daily_cigarettes is None:
                validation_errors.append({"field": "daily_cigarettes", "message": "喫煙者の場合、1日の喫煙本数は必須です"})
            if smoking_habits.cigarette_type is None:
                validation_errors.append({"field": "cigarette_type", "message": "喫煙者の場合、タバコの種類は必須です"})
        
        # 喫煙者または元喫煙者の喫煙年数チェック
        if smoking_habits.smoking_status in ["smoker", "ex_smoker"]:
            if smoking_habits.smoking_years is None:
                validation_errors.append({"field": "smoking_years", "message": "喫煙者または元喫煙者の場合、喫煙年数は必須です"})
        
        # 元喫煙者の禁煙開始時期チェック
        if smoking_habits.smoking_status == "ex_smoker":
            if smoking_habits.quit_date is None:
                validation_errors.append({"field": "quit_date", "message": "元喫煙者の場合、禁煙開始時期は必須です"})
        
        if validation_errors:
            error_response: Dict[str, Any] = {
                "code": "VALIDATION_ERROR",
                "message": "入力データに不正があります",
                "details": validation_errors
            }
            raise HTTPException(status_code=400, detail=error_response)
        
        # questionnaire_idを生成
        questionnaire_id = f"quest_{uuid.uuid4().hex[:12]}"
        
        # session_idが未指定の場合は生成
        session_id = smoking_habits.session_id or f"sess_{uuid.uuid4().hex[:12]}"
        
        # 現在の時刻を取得
        submitted_at = datetime.utcnow().isoformat() + "Z"
        
        # レスポンス用のデータ構造を作成
        response_smoking_habits = SmokingHabitsData(
            smoking_status=smoking_habits.smoking_status,
            daily_cigarettes=smoking_habits.daily_cigarettes,
            smoking_years=smoking_habits.smoking_years,
            quit_date=smoking_habits.quit_date,
            cigarette_type=smoking_habits.cigarette_type,
            tar_content=smoking_habits.tar_content,
            nicotine_content=smoking_habits.nicotine_content,
            quit_intention=smoking_habits.quit_intention,
            smoking_pattern=smoking_habits.smoking_pattern
        )
        
        # TODO: データベースに保存
        # await save_smoking_habits_to_db(questionnaire_id, session_id, smoking_habits)
        
        # レスポンスデータを構築
        response_data = SmokingHabitsResponseData(
            questionnaire_id=questionnaire_id,
            session_id=session_id,
            submitted_at=submitted_at,
            smoking_habits=response_smoking_habits
        )
        
        return SmokingHabitsResponse(data=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        # サーバーエラー
        error_response: Dict[str, Any] = {
            "code": "INTERNAL_ERROR",
            "message": "内部サーバーエラーが発生しました"
        }
        raise HTTPException(status_code=500, detail=error_response)

@router.get("/smoking-habits/{questionnaire_id}")
async def get_smoking_habits(questionnaire_id: str):
    """
    保存された喫煙習慣データを取得する
    
    Args:
        questionnaire_id: 問診ID
        
    Returns:
        SmokingHabitsResponse: 喫煙習慣データ
    """
    # TODO: データベースから取得
    # smoking_habits = await get_smoking_habits_from_db(questionnaire_id)
    # if not smoking_habits:
    #     raise HTTPException(status_code=404, detail="Questionnaire not found")
    
    # 暫定的なダミーレスポンス
    raise HTTPException(status_code=501, detail="Not implemented yet")