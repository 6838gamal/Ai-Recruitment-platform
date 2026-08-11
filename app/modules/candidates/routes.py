
"""Candidates module routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_profile
from app.modules.candidates.services import CandidateService
from app.utils.enhanced_templates import EnhancedJinja2Templates


router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"],
)

templates = EnhancedJinja2Templates(
    directory="app/templates"
)


# ============================================================
# Candidates List
# ============================================================

@router.get(
    "/",
    response_class=HTMLResponse,
    name="candidates:list",
)
async def list_candidates(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    service = CandidateService(db)

    candidates = service.get_candidates(
        company_id=current_user.company_id,
    )

    return templates.TemplateResponse(
        request,
        "candidates/list.html",
        {
            "request": request,
            "current_user": current_user,
            "candidates": candidates,
        },
    )


# ============================================================
# Create Candidate - Form
# ============================================================

@router.get(
    "/create",
    response_class=HTMLResponse,
    name="candidates:create",
)
async def create_candidate(
    request: Request,
    current_user=Depends(get_current_user_profile),
):
    return templates.TemplateResponse(
        request,
        "candidates/create.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


# ============================================================
# Create Candidate - Submit
# ============================================================

@router.post(
    "/create",
    name="candidates:create_submit",
)
async def create_candidate_submit(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    form = await request.form()

    print("========== CREATE CANDIDATE ==========")
    print("FORM:", dict(form))
    print("USER:", current_user)
    print("COMPANY ID:", current_user.company_id)

    full_name = str(form.get("name", "")).strip()
    email = str(form.get("email", "")).strip()

    if not full_name:
        return templates.TemplateResponse(
            request,
            "candidates/create.html",
            {
                "request": request,
                "current_user": current_user,
                "error": "Name is required.",
            },
            status_code=400,
        )

    if not email:
        return templates.TemplateResponse(
            request,
            "candidates/create.html",
            {
                "request": request,
                "current_user": current_user,
                "error": "Email is required.",
            },
            status_code=400,
        )

    # Split full name
    name_parts = full_name.split(maxsplit=1)

    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    try:
        service = CandidateService(db)

        candidate = service.create_candidate(
            company_id=current_user.company_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=str(form.get("phone", "")).strip() or None,
            location=str(form.get("location", "")).strip() or None,
            linkedin_url=str(form.get("linkedin_url", "")).strip() or None,
            portfolio_url=str(form.get("portfolio_url", "")).strip() or None,
            summary=str(form.get("summary", "")).strip() or None,
            status=str(form.get("status", "new")).strip() or "new",
            source=str(form.get("source", "")).strip() or None,
            avatar_url=str(form.get("avatar_url", "")).strip() or None,
        )

        print("CREATED CANDIDATE:", candidate.id)
        print("CREATED COMPANY:", candidate.company_id)

    except Exception as exc:
        db.rollback()

        print("========== CREATE CANDIDATE ERROR ==========")
        print(type(exc).__name__)
        print(str(exc))

        return templates.TemplateResponse(
            request,
            "candidates/create.html",
            {
                "request": request,
                "current_user": current_user,
                "error": f"Failed to create candidate: {exc}",
            },
            status_code=500,
        )

    return RedirectResponse(
        url=request.url_for("candidates:list"),
        status_code=303,
    )


# ============================================================
# View Candidate
# ============================================================

@router.get(
    "/{candidate_id}",
    response_class=HTMLResponse,
    name="candidates:view",
)
async def view_candidate(
    candidate_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    service = CandidateService(db)

    candidate = service.get_candidate(
        candidate_id=candidate_id,
        company_id=current_user.company_id,
    )

    if not candidate:
        return RedirectResponse(
            url=request.url_for("candidates:list"),
            status_code=303,
        )

    return templates.TemplateResponse(
        request,
        "candidates/view.html",
        {
            "request": request,
            "current_user": current_user,
            "candidate": candidate,
        },
    )


# ============================================================
# Edit Candidate - Form
# ============================================================

@router.get(
    "/{candidate_id}/edit",
    response_class=HTMLResponse,
    name="candidates:edit_form",
)
async def edit_candidate_form(
    candidate_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    service = CandidateService(db)

    candidate = service.get_candidate(
        candidate_id=candidate_id,
        company_id=current_user.company_id,
    )

    if not candidate:
        return RedirectResponse(
            url=request.url_for("candidates:list"),
            status_code=303,
        )

    return templates.TemplateResponse(
        request,
        "candidates/edit.html",
        {
            "request": request,
            "current_user": current_user,
            "candidate": candidate,
        },
    )


# ============================================================
# Edit Candidate - Submit
# ============================================================

@router.post(
    "/{candidate_id}/edit",
    name="candidates:edit_submit",
)
async def edit_candidate_submit(
    candidate_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    form = await request.form()

    service = CandidateService(db)

    candidate = service.update_candidate(
        candidate_id=candidate_id,
        company_id=current_user.company_id,
        first_name=str(form.get("first_name", "")).strip(),
        last_name=str(form.get("last_name", "")).strip(),
        email=str(form.get("email", "")).strip(),
        phone=str(form.get("phone", "")).strip() or None,
        location=str(form.get("location", "")).strip() or None,
        linkedin_url=str(form.get("linkedin_url", "")).strip() or None,
        portfolio_url=str(form.get("portfolio_url", "")).strip() or None,
        summary=str(form.get("summary", "")).strip() or None,
        status=str(form.get("status", "new")).strip() or "new",
        source=str(form.get("source", "")).strip() or None,
        avatar_url=str(form.get("avatar_url", "")).strip() or None,
    )

    if not candidate:
        return RedirectResponse(
            url=request.url_for("candidates:list"),
            status_code=303,
        )

    return RedirectResponse(
        url=request.url_for(
            "candidates:view",
            candidate_id=str(candidate.id),
        ),
        status_code=303,
    )


# ============================================================
# Delete Candidate
# ============================================================

@router.post(
    "/{candidate_id}/delete",
    name="candidates:delete",
)
async def delete_candidate(
    candidate_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    service = CandidateService(db)

    service.delete_candidate(
        candidate_id=candidate_id,
        company_id=current_user.company_id,
    )

    return RedirectResponse(
        url=request.url_for("candidates:list"),
        status_code=303,
    )
