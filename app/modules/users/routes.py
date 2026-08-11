from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
async def list_users():
    return {"message": "Users list endpoint"}
