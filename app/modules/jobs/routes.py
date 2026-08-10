"""Jobs module routes."""
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.core.permissions import Permission
from app.database import get_db
from app.dependencies import require_permission
from app.utils.inspect_model import get_model_fields_sqlalchemy
from app.utils.safe_jinja import templates
from app.utils.template_utils import sanitize_context
from app.modules.jobs.services import JobService
from app.modules.jobs.models import JobPosting

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get(
    "/",
    response_class=HTMLResponse,
    name="jobs:list",
)
async def job_list(
    request: Request,
    page: int = 1,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.VIEW_JOBS)),
):
    """List jobs page."""
    service = JobService(db)
    company_id = current_user.company_id

    jobs, total = service.list_jobs(
        company_id=company_id,
        status=status,
        page=page,
        per_page=25,
    )

    fields = get_model_fields_sqlalchemy(JobPosting)

    context = {
        "request": request,
        "jobs": jobs,
        "total": total,
        "page": page,
        "status": status,
        "current_user": current_user,
        "fields": fields,
    }

    return templates.TemplateResponse(
        request=request,
        name="jobs/list.html",
        context=sanitize_context(context),
    )


# --- Create routes BEFORE dynamic routes to avoid matching "create" as a dynamic job_id ---
@router.get(
    "/create",
    response_class=HTMLResponse,
    name="jobs:create",
)
async def job_create_get(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_JOBS)),
):
    """Render create job form."""
    fields = get_model_fields_sqlalchemy(JobPosting)

    # Create a mock job object with default values for the form
    class MockJob:
        title = ""
        status = "draft"
        description = ""
        requirements = ""
        responsibilities = ""
        employment_type = ""
        work_type = ""
        experience_min = ""
        experience_max = ""
        salary_min = ""
        salary_max = ""
        salary_currency = "USD"
        headcount = 1

    context = {
        "request": request,
        "fields": fields,
        "action": "create",
        "current_user": current_user,
        "error": None,
        "job": MockJob(),
    }

    return templates.TemplateResponse(
        request=request,
        name="jobs/form.html",
        context=sanitize_context(context),
    )


@router.post(
    "/create",
    name="jobs:create_post",
)
async def job_create_post(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    requirements: Optional[str] = Form(None),
    responsibilities: Optional[str] = Form(None),
    employment_type: Optional[str] = Form(None),
    work_type: Optional[str] = Form(None),
    experience_min: Optional[int] = Form(None),
    experience_max: Optional[int] = Form(None),
    salary_min: Optional[float] = Form(None),
    salary_max: Optional[float] = Form(None),
    salary_currency: str = Form("USD"),
    status: str = Form("draft"),
    headcount: int = Form(1),
    department_id: Optional[uuid.UUID] = Form(None),
    branch_id: Optional[uuid.UUID] = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_JOBS)),
):
    """Handle create job POST from form."""
    service = JobService(db)
    data = {
        "title": title.strip(),
        "description": description.strip(),
        "requirements": requirements,
        "responsibilities": responsibilities,
        "employment_type": employment_type,
        "work_type": work_type,
        "experience_min": experience_min,
        "experience_max": experience_max,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": salary_currency,
        "status": status,
        "headcount": headcount,
        "department_id": department_id,
        "branch_id": branch_id,
    }

    try:
        job = service.create_job(current_user, data)
        db.commit()
    except Exception as e:
        db.rollback()
        fields = get_model_fields_sqlalchemy(JobPosting)
        context = {
            "request": request,
            "fields": fields,
            "action": "create",
            "current_user": current_user,
            "error": str(e),
        }
        return templates.TemplateResponse(
            request=request,
            name="jobs/form.html",
            context=sanitize_context(context),
        )

    return RedirectResponse(url=f"/jobs/{job.id}", status_code=303)


# --- Dynamic routes (must come AFTER static routes like /create) ---
@router.get(
    "/{job_id}",
    response_class=HTMLResponse,
    name="jobs:view",
)
async def job_view(
    request: Request,
    job_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.VIEW_JOBS)),
):
    """Job detail view page."""
    service = JobService(db)

    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid job ID")

    job = service.get_job_by_id(job_uuid, current_user.company_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    fields = get_model_fields_sqlalchemy(JobPosting)

    context = {
        "request": request,
        "job": job,
        "current_user": current_user,
        "fields": fields,
    }

    return templates.TemplateResponse(
        request=request,
        name="jobs/view.html",
        context=sanitize_context(context),
    )


@router.get(
    "/{job_id}/edit",
    response_class=HTMLResponse,
    name="jobs:edit",
)
async def job_edit(
    request: Request,
    job_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_JOBS)),
):
    """Job edit page."""
    service = JobService(db)

    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid job ID")

    job = service.get_job_by_id(job_uuid, current_user.company_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    fields = get_model_fields_sqlalchemy(JobPosting)

    context = {
        "request": request,
        "job": job,
        "current_user": current_user,
        "fields": fields,
        "action": "edit",
    }

    return templates.TemplateResponse(
        request=request,
        name="jobs/form.html",
        context=sanitize_context(context),
    )


@router.post(
    "/{job_id}/edit",
    name="jobs:update_post",
)
async def job_update_post(
    request: Request,
    job_id: str,
    title: str = Form(...),
    description: str = Form(...),
    requirements: Optional[str] = Form(None),
    responsibilities: Optional[str] = Form(None),
    employment_type: Optional[str] = Form(None),
    work_type: Optional[str] = Form(None),
    experience_min: Optional[int] = Form(None),
    experience_max: Optional[int] = Form(None),
    salary_min: Optional[float] = Form(None),
    salary_max: Optional[float] = Form(None),
    salary_currency: str = Form("USD"),
    status: str = Form("draft"),
    headcount: int = Form(1),
    department_id: Optional[uuid.UUID] = Form(None),
    branch_id: Optional[uuid.UUID] = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_JOBS)),
):
    """Handle update job POST from form."""
    service = JobService(db)

    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid job ID")

    data = {
        "title": title.strip(),
        "description": description.strip(),
        "requirements": requirements,
        "responsibilities": responsibilities,
        "employment_type": employment_type,
        "work_type": work_type,
        "experience_min": experience_min,
        "experience_max": experience_max,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": salary_currency,
        "status": status,
        "headcount": headcount,
        "department_id": department_id,
        "branch_id": branch_id,
    }

    try:
        job = service.update_job(job_uuid, current_user.company_id, data)
    except Exception as e:
        db.rollback()
        job = service.get_job_by_id(job_uuid, current_user.company_id)
        fields = get_model_fields_sqlalchemy(JobPosting)
        context = {
            "request": request,
            "job": job,
            "fields": fields,
            "action": "edit",
            "current_user": current_user,
            "error": str(e),
        }
        return templates.TemplateResponse(
            request=request,
            name="jobs/form.html",
            context=sanitize_context(context),
        )

    return RedirectResponse(url=f"/jobs/{job.id}", status_code=303)


@router.post(
    "/{job_id}/delete",
    name="jobs:delete",
)
async def job_delete(
    request: Request,
    job_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_JOBS)),
):
    """Delete (soft-delete) a job posting."""
    service = JobService(db)

    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid job ID")

    try:
        service.delete_job(job_uuid, current_user.company_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return RedirectResponse(url="/jobs", status_code=303)
