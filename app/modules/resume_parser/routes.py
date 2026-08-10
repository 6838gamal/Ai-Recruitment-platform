from fastapi import APIRouter

router = APIRouter(prefix="/resume-parser", tags=["Resume Parser"])

@router.post("/parse")
async def parse_resume():
    return {"message": "Resume parser endpoint"}
