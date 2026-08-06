"""CRM module routes."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.permissions import Permission
from app.dependencies import require_permission

router = APIRouter(prefix="/crm", tags=["CRM"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="crm:list")
async def client_list(
    request: Request,
    current_user=Depends(require_permission(Permission.VIEW_COMPANIES)),
):
    return templates.TemplateResponse(request, "crm/list.html", {
        "current_user": current_user, "clients": []
    })
