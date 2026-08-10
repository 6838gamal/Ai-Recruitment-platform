from fastapi import APIRouter

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("/")
async def list_companies():
    return {"message": "Companies list endpoint"}
