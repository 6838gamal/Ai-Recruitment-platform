from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.utils.enhanced_templates import EnhancedJinja2Templates
from app.dependencies import get_current_user_profile

router = APIRouter(prefix="/crm", tags=["CRM"])
templates = EnhancedJinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def get_crm(request: Request, current_user = Depends(get_current_user_profile)):
    return templates.TemplateResponse(
        request,
        "crm/list.html",
        {"request": request, "current_user": current_user}
    )
