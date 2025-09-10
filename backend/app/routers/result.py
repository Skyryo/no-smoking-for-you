from fastapi import APIRouter

router = APIRouter()

@router.get("/result")
async def get_result():
    """Get diagnosis result endpoint - placeholder"""
    return {"message": "Result endpoint - not implemented yet"}
