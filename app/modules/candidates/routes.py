"""Candidates module routes."""

import uuid
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.database import get_db
from app.dependencies import require_permission
from app.utils.inspect_model import get_model_fields_sqlalchemy
from app.utils.safe_jinja import templates
from app.utils.template_utils import sanitize_context

from app.modules.candidates.models import Candidate
from app.modules.candidates.services import CandidateService


router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.get(
    "/",
    response_class=HTMLResponse,
    name="candidates:list",
)
async def candidate_list(
    request: Request,
    page: int = 1,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.VIEW_CANDIDATES)),
):
    """Candidates list page (paginated)."""
    service = CandidateService(db)
    per_page = 25
    skip = (page - 1) * per_page
    candidates = service.get_all_candidates(company_id=current_user.company_id, skip=skip, limit=per_page)

    # get_model_fields_sqlalchemy returns list[dict], convert to list[str] names for templates
    fields = [col["name"] for col in get_model_fields_sqlalchemy(Candidate)]

    context = {
        "request": request,
        "candidates": candidates,
        "total": len(candidates),
        "page": page,
        "current_user": current_user,
        "fields": fields,
    }

    return templates.TemplateResponse(request=request, name="candidates/list.html", context=sanitize_context(context))


@router.get(
    "/{candidate_id}",
    response_class=HTMLResponse,
    name="candidates:view",
)
async def candidate_view(
    request: Request,
    candidate_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.VIEW_CANDIDATES)),
):
    """Candidate detail view."""
    try:
        candidate_uuid = uuid.UUID(candidate_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid candidate ID")

    service = CandidateService(db)
    candidate = service.get_candidate_by_id(candidate_uuid, current_user.company_id)

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # convert fields to simple names for templates
    fields = [col["name"] for col in get_model_fields_sqlalchemy(Candidate)]

    context = {
        "request": request,
        "candidate": candidate,
        "current_user": current_user,
        "fields": fields,
    }

    return templates.TemplateResponse(request=request, name="candidates/view.html", context=sanitize_context(context))


@router.get(
    "/create",
    response_class=HTMLResponse,
    name="candidates:create",
)
async def candidate_create_form(
    request: Request,
    current_user=Depends(require_permission(Permission.MANAGE_CANDIDATES)),
):
    """Render candidate creation form."""
    # convert fields to simple names for templates
    fields = [col["name"] for col in get_model_fields_sqlalchemy(Candidate)]

    context = {
        "request": request,
        "current_user": current_user,
        "fields": fields,
    }

    return templates.TemplateResponse(request=request, name="candidates/create.html", context=sanitize_context(context))


@router.post("/create")
async def candidate_create_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_CANDIDATES)),
):
    """Handle candidate creation form submit and save to DB."""
    service = CandidateService(db)

    # Basic name split into first/last
    if " " in name.strip():
        first_name, last_name = name.strip().split(" ", 1)
    else:
        first_name = name.strip()
        last_name = ""

    try:
        candidate = service.create_candidate(
            company_id=current_user.company_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
    except Exception:
        db.rollback()
        raise

    return RedirectResponse(url=f"/candidates/{candidate.id}", status_code=303)
