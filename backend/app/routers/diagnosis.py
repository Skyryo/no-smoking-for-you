from fastapi import APIRouter

router = APIRouter()

@router.get("/diagnosis")
async def get_diagnosis():
    """AI diagnosis endpoint - placeholder"""
    return {"message": "Diagnosis endpoint - not implemented yet"}
