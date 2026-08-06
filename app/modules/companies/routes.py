"""Companies module routes."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.database import get_db
from app.dependencies import require_permission

router = APIRouter(prefix="/companies", tags=["Companies"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="companies:list")
async def company_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.VIEW_COMPANIES)),
):
    return templates.TemplateResponse("companies/list.html", {
        "request": request, "current_user": current_user
    })
