from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.utils.enhanced_templates import EnhancedJinja2Templates
from app.dependencies import get_current_user_profile

router = APIRouter(prefix="/reports", tags=["Reports"])
templates = EnhancedJinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def list_reports(request: Request, current_user = Depends(get_current_user_profile)):
    return templates.TemplateResponse(
        request,
        "reports/list.html",
        {"request": request, "current_user": current_user}
    )
