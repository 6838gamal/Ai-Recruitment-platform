"""Jobs module routes."""
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
import uuid

from app.core.permissions import Permission
from app.database import get_db
from app.dependencies import require_permission
from app.utils.inspect_model import get_model_fields_sqlalchemy
from app.modules.jobs.services import JobService
from app.modules.jobs.models import JobPosting

router = APIRouter(prefix="/jobs", tags=["Jobs"])
templates = Jinja2Templates(directory="app/templates")


# Ensure `attribute` helper is available in Jinja globals so templates can call attribute(obj, name)
if "attribute" not in templates.env.globals:
    templates.env.globals["attribute"] = getattr


def render_template(request: Request, name: str, context: dict | None = None):
    """
    Safe helper to render templates: ensures context is a plain dict and always includes the request.
    Use this instead of calling templates.TemplateResponse(...) directly from routes.
    """
    if context is None:
        context = {}
    # Defensive: convert non-dict contexts (e.g., sequence of pairs) into dict
    if not isinstance(context, dict):
        try:
            context = dict(context)
        except Exception:
            context = {}
    ctx = {"request": request, **context}
    # Use the newer TemplateResponse signature (request first)
    return templates.TemplateResponse(request, name, ctx)


@router.get("/", response_class=HTMLResponse, name="jobs:list")
async def job_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.VIEW_JOBS)),
):
    service = JobService(db)
    # For now list is company-scoped; attempt to derive company_id from current_user if present
    company_id = getattr(current_user, "company_id", None)
    jobs = service.get_all_jobs(company_id) if company_id else []
    return render_template(request, "jobs/list.html", {"current_user": current_user, "jobs": jobs})


@router.get("/create", response_class=HTMLResponse, name="jobs:create")
async def job_create_get(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_JOBS)),
):
    """Render create job form."""
    fields = get_model_fields_sqlalchemy(JobPosting)
    return render_template(
        request,
        "jobs/form.html",
        {
            "fields": fields,
            "action": "create",
            "current_user": current_user,
            "error": None,
        },
    )


@router.post("/create")
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
        return render_template(
            request,
            "jobs/form.html",
            {
                "fields": fields,
                "action": "create",
                "current_user": current_user,
                "error": str(e),
            },
        )

    return RedirectResponse(url=f"/jobs/{job.id}", status_code=303)
