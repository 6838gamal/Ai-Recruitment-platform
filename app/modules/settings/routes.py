"""Settings module routes."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.permissions import Permission
from app.dependencies import require_permission

router = APIRouter(prefix="/settings", tags=["Settings"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="settings:index")
async def settings_index(
    request: Request,
    current_user=Depends(require_permission(Permission.MANAGE_SETTINGS)),
):
    return templates.TemplateResponse("settings/index.html", {
        "request": request, "current_user": current_user
    })
