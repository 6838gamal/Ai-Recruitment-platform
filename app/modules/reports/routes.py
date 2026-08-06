"""Reports module routes."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.permissions import Permission
from app.dependencies import require_permission

router = APIRouter(prefix="/reports", tags=["Reports"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="reports:index")
async def reports_index(
    request: Request,
    current_user=Depends(require_permission(Permission.VIEW_REPORTS)),
):
    return templates.TemplateResponse("reports/index.html", {
        "request": request, "current_user": current_user
    })
