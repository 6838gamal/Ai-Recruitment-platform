"""Candidates module routes."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
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
    return templates.TemplateResponse("candidates/list.html", {
        "current_user": current_user, "candidates": []
    })


@router.get("/create", response_class=HTMLResponse, name="candidates:create")
async def candidate_create_form(request: Request):
    """Render candidate creation form."""
    return templates.TemplateResponse("candidates/create.html", {"request": request})


@router.post("/create")
async def candidate_create_submit(request: Request):
    """Handle candidate form submission (minimal placeholder).
    Implement saving logic in services when ready.
    """
    # Placeholder: redirect back to list. Expand to accept Form fields and save to DB.
    return RedirectResponse(url="/candidates", status_code=303)
