"""Audit module routes."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.permissions import Permission
from app.dependencies import require_permission

router = APIRouter(prefix="/audit", tags=["Audit"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="audit:logs")
async def audit_logs(
    request: Request,
    current_user=Depends(require_permission(Permission.VIEW_AUDIT_LOGS)),
):
    return templates.TemplateResponse("audit/list.html", {
        "request": request, "current_user": current_user, "logs": []
    })
