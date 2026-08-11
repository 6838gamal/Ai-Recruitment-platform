from fastapi import APIRouter

router = APIRouter(prefix="/candidates", tags=["Candidates"])

@router.get("/")
async def list_candidates():
    return {"message": "Candidates list endpoint"}
