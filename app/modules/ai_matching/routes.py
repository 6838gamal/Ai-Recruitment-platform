from fastapi import APIRouter

router = APIRouter(prefix="/ai-matching", tags=["AI Matching"])

@router.get("/")
async def get_matching():
    return {"message": "AI Matching endpoint"}
