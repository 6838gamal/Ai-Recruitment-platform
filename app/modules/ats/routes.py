"""ATS module routes."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.permissions import Permission
from app.dependencies import require_permission

router = APIRouter(prefix="/ats", tags=["ATS"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/{job_id}", response_class=HTMLResponse, name="ats:pipeline")
async def pipeline(
    request: Request,
    job_id: str,
    current_user=Depends(require_permission(Permission.VIEW_JOBS)),
):
    return templates.TemplateResponse(request, "ats/pipeline.html", {
        "current_user": current_user, "job_id": job_id
    })
