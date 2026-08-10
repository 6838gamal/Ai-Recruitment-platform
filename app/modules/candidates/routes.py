"""Candidates module routes."""

from uuid import UUID
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

    # service.get_all_candidates returns (candidates, total)
    candidates, total = service.get_all_candidates(company_id=current_user.company_id, skip=skip, limit=per_page)

    # pass full metadata (list[dict]) in case templates expect it
    fields = get_model_fields_sqlalchemy(Candidate)

    context = {
        "request": request,
        "candidates": candidates,
        "total": total,
        "page": page,
        "current_user": current_user,
        "fields": fields,
    }

    return templates.TemplateResponse(request=request, name="candidates/list.html", context=sanitize_context(context))


# --- Create routes first to avoid matching "create" as a dynamic candidate_id ---
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
    fields = get_model_fields_sqlalchemy(Candidate)

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


# --- Dynamic candidate routes (use UUID type so FastAPI validates input) ---
@router.get(
    "/{candidate_id}",
    response_class=HTMLResponse,
    name="candidates:view",
)
async def candidate_view(
    request: Request,
    candidate_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.VIEW_CANDIDATES)),
):
    """Candidate detail view."""
    # candidate_id is already a uuid.UUID instance (validated by FastAPI)
    service = CandidateService(db)
    candidate = service.get_candidate_by_id(candidate_id, current_user.company_id)

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    fields = get_model_fields_sqlalchemy(Candidate)

    context = {
        "request": request,
        "candidate": candidate,
        "current_user": current_user,
        "fields": fields,
    }

    return templates.TemplateResponse(request=request, name="candidates/view.html", context=sanitize_context(context))


# --- Edit form (GET) ---
@router.get("/{candidate_id}/edit", response_class=HTMLResponse, name="candidates:edit_form")
async def candidate_edit_form(
    request: Request,
    candidate_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_CANDIDATES)),
):
    service = CandidateService(db)
    candidate = service.get_candidate_by_id(candidate_id, current_user.company_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    fields = get_model_fields_sqlalchemy(Candidate)
    context = {"request": request, "candidate": candidate, "current_user": current_user, "fields": fields}
    return templates.TemplateResponse(request=request, name="candidates/edit.html", context=sanitize_context(context))


# --- Edit submit (POST) ---
@router.post("/{candidate_id}/edit", name="candidates:edit_submit")
async def candidate_edit_submit(
    request: Request,
    candidate_id: UUID,
    first_name: str = Form(...),
    last_name: str = Form(""),
    email: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_CANDIDATES)),
):
    service = CandidateService(db)
    updated = service.update_candidate(candidate_id, current_user.company_id, first_name=first_name, last_name=last_name, email=email)
    if not updated:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return RedirectResponse(url=request.url_for("candidates:view", candidate_id=str(candidate_id)), status_code=303)


# --- Delete (soft delete) ---
@router.post("/{candidate_id}/delete", name="candidates:delete")
async def candidate_delete(
    request: Request,
    candidate_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_CANDIDATES)),
):
    service = CandidateService(db)
    deleted = service.delete_candidate(candidate_id, current_user.company_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return RedirectResponse(url=request.url_for("candidates:list"), status_code=303)
