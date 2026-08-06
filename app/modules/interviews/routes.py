"""Interviews module routes."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.permissions import Permission
from app.dependencies import require_permission

router = APIRouter(prefix="/interviews", tags=["Interviews"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="interviews:list")
async def interview_list(
    request: Request,
    current_user=Depends(require_permission(Permission.VIEW_INTERVIEWS)),
):
    return templates.TemplateResponse("interviews/list.html", {
        "request": request, "current_user": current_user, "interviews": []
    })
