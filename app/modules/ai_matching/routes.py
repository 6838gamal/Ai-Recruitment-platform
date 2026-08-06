"""AI Matching module routes."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.permissions import Permission
from app.dependencies import require_permission

router = APIRouter(prefix="/ai-matching", tags=["AI Matching"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="ai_matching:index")
async def ai_matching_index(
    request: Request,
    current_user=Depends(require_permission(Permission.USE_AI_MATCHING)),
):
    return templates.TemplateResponse("ai_matching/index.html", {
        "request": request, "current_user": current_user
    })
