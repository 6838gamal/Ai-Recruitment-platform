from fastapi import APIRouter

router = APIRouter(prefix="/interviews", tags=["Interviews"])

@router.get("/")
async def list_interviews():
    return {"message": "Interviews list endpoint"}
