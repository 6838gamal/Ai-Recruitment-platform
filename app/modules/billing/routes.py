from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/billing", tags=["Billing"]) 

@router.get("/")
async def get_billing():
    # Return a proper JSONResponse instead of a raw dict for clarity
    return JSONResponse({"message": "Billing endpoint"})
