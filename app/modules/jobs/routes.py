
"""Jobs module routes."""

from pathlib import Path
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_profile
from app.modules.jobs.models import JobPosting
from app.utils.enhanced_templates import EnhancedJinja2Templates


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)

templates = EnhancedJinja2Templates(
    directory="app/templates"
)


# ---------------------------------------------------------------------------
# Template helper
# ---------------------------------------------------------------------------

def _job_template(preferred: str, fallback: str) -> str:
    """Pick an existing jobs template."""

    project_root = Path(__file__).resolve().parents[2]
    templates_dir = project_root / "templates"

    preferred_path = templates_dir / preferred

    if preferred_path.exists():
        return preferred

    fallback_path = templates_dir / fallback

    if fallback_path.exists():
        return fallback

    return preferred


# ---------------------------------------------------------------------------
# Jobs list
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_class=HTMLResponse,
)
async def list_jobs(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Render the jobs list page."""

    jobs = (
        db.query(JobPosting)
        .order_by(JobPosting.id.desc())
        .all()
    )

    return templates.TemplateResponse(
        request,
        "jobs/list.html",
        {
            "request": request,
            "current_user": current_user,
            "jobs": jobs,
        },
    )


# ---------------------------------------------------------------------------
# Create job form
# ---------------------------------------------------------------------------

@router.get(
    "/create",
    response_class=HTMLResponse,
)
async def create_job_form(
    request: Request,
    current_user=Depends(get_current_user_profile),
):
    """Render the job creation form."""

    template = _job_template(
        "jobs/form.html",
        "jobs/create.html",
    )

    job = {}

    return templates.TemplateResponse(
        request,
        template,
        {
            "request": request,
            "current_user": current_user,
            "job": job,
            "action": "create",
        },
    )


# ---------------------------------------------------------------------------
# Create job
# ---------------------------------------------------------------------------

@router.post(
    "/create",
)
async def create_job_submit(
    request: Request,
    title: str = Form(...),
    location: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    status: str = Form("draft"),
    company_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Create a new job posting."""

    template = _job_template(
        "jobs/form.html",
        "jobs/create.html",
    )

    # -----------------------------------------------------------------------
    # Validate title
    # -----------------------------------------------------------------------

    title = title.strip()

    if not title:
        job_context = {
            "title": "",
            "location": location or "",
            "description": description or "",
            "status": status or "draft",
            "company_id": company_id or "",
        }

        return templates.TemplateResponse(
            request,
            template,
            {
                "request": request,
                "current_user": current_user,
                "error": "Job title is required.",
                "job": job_context,
                "action": "create",
            },
            status_code=400,
        )

    # -----------------------------------------------------------------------
    # Validate status
    # -----------------------------------------------------------------------

    allowed_statuses = {
        "draft",
        "published",
        "closed",
    }

    if status not in allowed_statuses:
        status = "draft"

    # -----------------------------------------------------------------------
    # Parse company_id
    # -----------------------------------------------------------------------

    parsed_company_id: Optional[UUID] = None

    if company_id:
        try:
            parsed_company_id = UUID(company_id)
        except ValueError:
            job_context = {
                "title": title,
                "location": location or "",
                "description": description or "",
                "status": status,
                "company_id": company_id,
            }

            return templates.TemplateResponse(
                request,
                template,
                {
                    "request": request,
                    "current_user": current_user,
                    "error": "Invalid company ID.",
                    "job": job_context,
                    "action": "create",
                },
                status_code=400,
            )

    # -----------------------------------------------------------------------
    # Create database object
    # -----------------------------------------------------------------------

    job = JobPosting(
        title=title,
        description=description.strip() if description else None,
        location=location.strip() if location else None,
        status=status,
        company_id=parsed_company_id,
    )

    # -----------------------------------------------------------------------
    # Save to database
    # -----------------------------------------------------------------------

    try:
        db.add(job)
        db.commit()
        db.refresh(job)

    except Exception as exc:
        db.rollback()

        job_context = {
            "title": title,
            "location": location or "",
            "description": description or "",
            "status": status,
            "company_id": company_id or "",
        }

        return templates.TemplateResponse(
            request,
            template,
            {
                "request": request,
                "current_user": current_user,
                "error": f"Failed to create job: {exc}",
                "job": job_context,
                "action": "create",
            },
            status_code=500,
        )

    # -----------------------------------------------------------------------
    # Redirect to jobs list
    # -----------------------------------------------------------------------

    return RedirectResponse(
        url="/jobs/",
        status_code=303,
    )


# ---------------------------------------------------------------------------
# Job details
# ---------------------------------------------------------------------------

@router.get(
    "/{job_id}",
    response_class=HTMLResponse,
)
async def job_detail(
    job_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Render a single job."""

    job = (
        db.query(JobPosting)
        .filter(JobPosting.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return templates.TemplateResponse(
        request,
        "jobs/detail.html",
        {
            "request": request,
            "current_user": current_user,
            "job": job,
        },
    )


# ---------------------------------------------------------------------------
# Edit job form
# ---------------------------------------------------------------------------

@router.get(
    "/{job_id}/edit",
    response_class=HTMLResponse,
)
async def edit_job_form(
    job_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Render the edit job form."""

    job = (
        db.query(JobPosting)
        .filter(JobPosting.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    template = _job_template(
        "jobs/form.html",
        "jobs/create.html",
    )

    return templates.TemplateResponse(
        request,
        template,
        {
            "request": request,
            "current_user": current_user,
            "job": job,
            "action": "edit",
        },
    )


# ---------------------------------------------------------------------------
# Update job
# ---------------------------------------------------------------------------

@router.post(
    "/{job_id}/edit",
)
async def edit_job_submit(
    job_id: UUID,
    request: Request,
    title: str = Form(...),
    location: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    status: str = Form("draft"),
    company_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Update an existing job."""

    job = (
        db.query(JobPosting)
        .filter(JobPosting.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    template = _job_template(
        "jobs/form.html",
        "jobs/create.html",
    )

    # Validate title
    title = title.strip()

    if not title:
        return templates.TemplateResponse(
            request,
            template,
            {
                "request": request,
                "current_user": current_user,
                "error": "Job title is required.",
                "job": job,
                "action": "edit",
            },
            status_code=400,
        )

    # Validate status
    allowed_statuses = {
        "draft",
        "published",
        "closed",
    }

    if status not in allowed_statuses:
        status = "draft"

    # Parse company ID
    parsed_company_id: Optional[UUID] = None

    if company_id:
        try:
            parsed_company_id = UUID(company_id)
        except ValueError:
            return templates.TemplateResponse(
                request,
                template,
                {
                    "request": request,
                    "current_user": current_user,
                    "error": "Invalid company ID.",
                    "job": job,
                    "action": "edit",
                },
                status_code=400,
            )

    # Update object
    job.title = title
    job.description = (
        description.strip()
        if description
        else None
    )
    job.location = (
        location.strip()
        if location
        else None
    )
    job.status = status
    job.company_id = parsed_company_id

    try:
        db.commit()
        db.refresh(job)

    except Exception as exc:
        db.rollback()

        return templates.TemplateResponse(
            request,
            template,
            {
                "request": request,
                "current_user": current_user,
                "error": f"Failed to update job: {exc}",
                "job": job,
                "action": "edit",
            },
            status_code=500,
        )

    return RedirectResponse(
        url="/jobs/",
        status_code=303,
    )


# ---------------------------------------------------------------------------
# Delete job
# ---------------------------------------------------------------------------

@router.post(
    "/{job_id}/delete",
)
async def delete_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Delete a job."""

    job = (
        db.query(JobPosting)
        .filter(JobPosting.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    try:
        db.delete(job)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return RedirectResponse(
        url="/jobs/",
        status_code=303,
    )
