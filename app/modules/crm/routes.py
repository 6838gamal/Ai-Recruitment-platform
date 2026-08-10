from fastapi import APIRouter

router = APIRouter(prefix="/crm", tags=["CRM"])

@router.get("/")
async def get_crm():
    return {"message": "CRM endpoint"}
