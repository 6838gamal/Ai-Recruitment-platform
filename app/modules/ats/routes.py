from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.dependencies import get_current_user_profile

router = APIRouter(prefix="/ats", tags=["ATS"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def get_ats(request: Request, current_user = Depends(get_current_user_profile)):
    return templates.TemplateResponse(
        request,
        "ats/list.html",
        {"request": request, "current_user": current_user}
    )
