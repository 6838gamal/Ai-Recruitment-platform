from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, current_user = Depends(get_current_user)):
    return templates.TemplateResponse(
        request, 
        "dashboard/index.html", 
        {
            "request": request,
            "current_user": current_user
        }
    )
