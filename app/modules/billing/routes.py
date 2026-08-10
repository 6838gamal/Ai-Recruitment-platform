from fastapi import APIRouter

router = APIRouter(prefix="/billing", tags=["Billing"])

@router.get("/")
async def get_billing():
    return {"message": "Billing endpoint"}
