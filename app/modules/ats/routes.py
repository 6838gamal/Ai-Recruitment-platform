from fastapi import APIRouter

router = APIRouter(prefix="/ats", tags=["ATS"])

@router.get("/")
async def get_ats():
    return {"message": "ATS endpoint"}
