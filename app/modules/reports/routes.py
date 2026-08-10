from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/")
async def list_reports():
    return {"message": "Reports list endpoint"}
