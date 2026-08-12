"""Jobs module routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import (
    get_current_user_id,
    get_current_user_profile,
)
from app.modules.jobs.models import JobPosting
from app.utils.enhanced_templates import EnhancedJinja2Templates


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)

templates = EnhancedJinja2Templates(
    directory="app/templates"
)


# ============================================================
# HELPERS
# ============================================================

def get_companies(db: Session):
    """
    Return all active companies.

    This helper keeps company loading in one place and prevents
    template errors when the company query fails.
    """

    try:
        from app.modules.companies.models import Company

        return (
            db.query(Company)
            .filter(
                Company.deleted_at.is_(None)
            )
            .order_by(
                Company.name.asc()
            )
            .all()
        )

    except Exception:
        return []


async def render_create_job_form(
    request: Request,
    db: Session,
    current_user,
    error: str | None = None,
    form_values=None,
    status_code: int = 200,
):
    """
    Render the create job page.

    Used both for the initial GET request and when validation
    or database errors occur.
    """

    companies = get_companies(db)

    return templates.TemplateResponse(
        request,
        "jobs/create.html",
        {
            "request": request,
            "current_user": current_user,
            "companies": companies,
            "error": error,
            "form_values": form_values,
        },
        status_code=status_code,
    )


# ============================================================
# JOBS LIST
# ============================================================

@router.get(
    "/",
    response_class=HTMLResponse,
    name="jobs:list",
)
async def list_jobs(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """
    Display all active job postings.

    Jobs are filtered by the current user's company when a
    company is available.
    """

    query = (
        db.query(JobPosting)
        .filter(
            JobPosting.deleted_at.is_(None)
        )
    )

    # --------------------------------------------------------
    # Company filtering
    # --------------------------------------------------------

    company_id = getattr(
        current_user,
        "company_id",
        None,
    )

    if company_id:
        query = query.filter(
            JobPosting.company_id == company_id
        )

    jobs = (
        query
        .order_by(
            JobPosting.created_at.desc()
        )
        .all()
    )

    return templates.TemplateResponse(
        request,
        "jobs/list.html",
        {
            "request": request,
            "jobs": jobs,
            "current_user": current_user,
        },
    )


# ============================================================
# CREATE JOB FORM
# ============================================================

@router.get(
    "/create",
    response_class=HTMLResponse,
    name="jobs:create_form",
)
async def create_job_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """
    Display the create job form.
    """

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="You must be logged in to create a job.",
        )

    return await render_create_job_form(
        request=request,
        db=db,
        current_user=current_user,
    )


# ============================================================
# CREATE JOB
# ============================================================

@router.post(
    "/create",
)
async def create_job_submit(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
    current_user_id: UUID = Depends(get_current_user_id),
):
    """
    Create a new job posting.

    IMPORTANT:
    created_by_id is taken directly from the authenticated
    JWT's `sub` claim through get_current_user_id().

    It MUST NOT depend on current_user.user_id.
    """

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="You must be logged in to create a job.",
        )

    # --------------------------------------------------------
    # Authenticated User ID
    # --------------------------------------------------------

    if not current_user_id:
        raise HTTPException(
            status_code=401,
            detail=(
                "Unable to determine the authenticated "
                "user ID."
            ),
        )

    # --------------------------------------------------------
    # Read form
    # --------------------------------------------------------

    form = await request.form()

    title = str(
        form.get("title") or ""
    ).strip()

    description = str(
        form.get("description") or ""
    ).strip()

    location = str(
        form.get("location") or ""
    ).strip()

    status = str(
        form.get("status") or "draft"
    ).strip().lower()

    company_id_raw = str(
        form.get("company_id") or ""
    ).strip()

    # --------------------------------------------------------
    # Validate title
    # --------------------------------------------------------

    if not title:
        return await render_create_job_form(
            request=request,
            db=db,
            current_user=current_user,
            error="Job title is required.",
            form_values=form,
            status_code=400,
        )

    # --------------------------------------------------------
    # Validate status
    # --------------------------------------------------------

    allowed_statuses = {
        "draft",
        "published",
        "closed",
        "archived",
    }

    if status not in allowed_statuses:
        status = "draft"

    # --------------------------------------------------------
    # Resolve company
    # --------------------------------------------------------

    company_id = None

    if company_id_raw:
        try:
            company_id = UUID(
                company_id_raw
            )

        except ValueError:
            return await render_create_job_form(
                request=request,
                db=db,
                current_user=current_user,
                error="Invalid company ID.",
                form_values=form,
                status_code=400,
            )

    else:
        # If the user didn't select a company,
        # use the user's company.
        company_id = getattr(
            current_user,
            "company_id",
            None,
        )

    # --------------------------------------------------------
    # IMPORTANT AUTHENTICATION FIX
    # --------------------------------------------------------
    #
    # `current_user` is UserProfile.
    #
    # UserProfile:
    #
    #     id       -> user_profiles.id
    #     user_id  -> users.id
    #
    # JobPosting.created_by_id:
    #
    #     -> users.id
    #
    # Therefore we use current_user_id, which comes directly
    # from JWT.sub.
    #
    # --------------------------------------------------------

    created_by_id = current_user_id

    # --------------------------------------------------------
    # Final safety check
    # --------------------------------------------------------

    if not created_by_id:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user ID is missing.",
        )

    # --------------------------------------------------------
    # Create JobPosting
    # --------------------------------------------------------

    job = JobPosting(
        title=title,
        description=description or None,
        location=location or None,
        status=status,
        company_id=company_id,
        created_by_id=created_by_id,
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    try:
        db.add(job)

        db.commit()

        db.refresh(job)

    except IntegrityError as exc:
        db.rollback()

        error = (
            str(exc.orig)
            if exc.orig
            else str(exc)
        )

        return await render_create_job_form(
            request=request,
            db=db,
            current_user=current_user,
            error=error,
            form_values=form,
            status_code=400,
        )

    except Exception:
        db.rollback()
        raise

    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    return RedirectResponse(
        url="/jobs/",
        status_code=303,
    )


# ============================================================
# JOB DETAIL
# ============================================================

@router.get(
    "/{job_id}",
    response_class=HTMLResponse,
    name="jobs:detail",
)
async def job_detail(
    request: Request,
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """
    Display a single job posting.
    """

    job = (
        db.query(JobPosting)
        .filter(
            JobPosting.id == job_id,
            JobPosting.deleted_at.is_(None),
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    return templates.TemplateResponse(
        request,
        "jobs/detail.html",
        {
            "request": request,
            "job": job,
            "current_user": current_user,
        },
    )


# ============================================================
# EDIT JOB FORM
# ============================================================

@router.get(
    "/{job_id}/edit",
    response_class=HTMLResponse,
    name="jobs:edit_form",
)
async def edit_job_form(
    request: Request,
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """
    Display edit job form.
    """

    job = (
        db.query(JobPosting)
        .filter(
            JobPosting.id == job_id,
            JobPosting.deleted_at.is_(None),
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    companies = get_companies(db)

    return templates.TemplateResponse(
        request,
        "jobs/edit.html",
        {
            "request": request,
            "job": job,
            "companies": companies,
            "current_user": current_user,
        },
    )


# ============================================================
# EDIT JOB
# ============================================================

@router.post(
    "/{job_id}/edit",
)
async def edit_job_submit(
    request: Request,
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """
    Update an existing job posting.
    """

    job = (
        db.query(JobPosting)
        .filter(
            JobPosting.id == job_id,
            JobPosting.deleted_at.is_(None),
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    form = await request.form()

    title = str(
        form.get("title") or job.title
    ).strip()

    description = str(
        form.get("description")
        if form.get("description") is not None
        else (job.description or "")
    ).strip()

    location = str(
        form.get("location")
        if form.get("location") is not None
        else (job.location or "")
    ).strip()

    status = str(
        form.get("status")
        if form.get("status") is not None
        else job.status
    ).strip().lower()

    company_id_raw = str(
        form.get("company_id") or ""
    ).strip()

    # --------------------------------------------------------
    # Validate title
    # --------------------------------------------------------

    if not title:
        companies = get_companies(db)

        return templates.TemplateResponse(
            request,
            "jobs/edit.html",
            {
                "request": request,
                "job": job,
                "companies": companies,
                "current_user": current_user,
                "error": "Job title is required.",
                "form_values": form,
            },
            status_code=400,
        )

    # --------------------------------------------------------
    # Validate status
    # --------------------------------------------------------

    allowed_statuses = {
        "draft",
        "published",
        "closed",
        "archived",
    }

    if status not in allowed_statuses:
        status = "draft"

    # --------------------------------------------------------
    # Company
    # --------------------------------------------------------

    if company_id_raw:
        try:
            company_id = UUID(
                company_id_raw
            )

        except ValueError:
            companies = get_companies(db)

            return templates.TemplateResponse(
                request,
                "jobs/edit.html",
                {
                    "request": request,
                    "job": job,
                    "companies": companies,
                    "current_user": current_user,
                    "error": "Invalid company ID.",
                    "form_values": form,
                },
                status_code=400,
            )

    else:
        company_id = getattr(
            current_user,
            "company_id",
            None,
        )

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    job.title = title
    job.description = description or None
    job.location = location or None
    job.status = status
    job.company_id = company_id

    try:
        db.commit()

        db.refresh(job)

    except IntegrityError as exc:
        db.rollback()

        error = (
            str(exc.orig)
            if exc.orig
            else str(exc)
        )

        companies = get_companies(db)

        return templates.TemplateResponse(
            request,
            "jobs/edit.html",
            {
                "request": request,
                "job": job,
                "companies": companies,
                "current_user": current_user,
                "error": error,
                "form_values": form,
            },
            status_code=400,
        )

    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    return RedirectResponse(
        url=f"/jobs/{job.id}",
        status_code=303,
    )


# ============================================================
# DELETE JOB
# ============================================================

@router.post(
    "/{job_id}/delete",
)
async def delete_job(
    request: Request,
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """
    Soft-delete a job posting.
    """

    job = (
        db.query(JobPosting)
        .filter(
            JobPosting.id == job_id,
            JobPosting.deleted_at.is_(None),
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    job.soft_delete()

    db.commit()

    return RedirectResponse(
        url="/jobs/",
        status_code=303,
    )
