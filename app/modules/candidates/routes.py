"""Candidates module routes."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.permissions import Permission
from app.database import get_db
from app.dependencies import require_permission

router = APIRouter(prefix="/candidates", tags=["Candidates"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="candidates:list")
async def candidate_list(
    request: Request,
    current_user=Depends(require_permission(Permission.VIEW_CANDIDATES)),
):
    return templates.TemplateResponse(request, "candidates/list.html", {
        "current_user": current_user, "candidates": []
    })
