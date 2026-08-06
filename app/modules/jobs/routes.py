"""Jobs module routes."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.database import get_db
from app.dependencies import require_permission

router = APIRouter(prefix="/jobs", tags=["Jobs"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="jobs:list")
async def job_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.VIEW_JOBS)),
):
    return templates.TemplateResponse(request, "jobs/list.html", {
        "current_user": current_user, "jobs": []
    })
