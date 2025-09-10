from fastapi import APIRouter

router = APIRouter()

@router.get("/questionnaire")
async def get_questionnaire():
    """Get questionnaire structure - placeholder"""
    return {"message": "Questionnaire endpoint - not implemented yet"}
