from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.utils.enhanced_templates import EnhancedJinja2Templates
from app.dependencies import get_current_user_profile
from pathlib import Path
from typing import Optional

router = APIRouter(prefix="/jobs", tags=["Jobs"])
templates = EnhancedJinja2Templates(directory="app/templates")

# Helper to pick a template name that exists under app/templates/jobs
def _job_template(preferred: str, fallback: str) -> str:
    project_root = Path(__file__).resolve().parents[2]
    templates_dir = project_root / "templates"
    preferred_path = templates_dir / preferred
    if preferred_path.exists():
        return preferred
    fallback_path = templates_dir / fallback
    if fallback_path.exists():
        return fallback
    # last resort: return preferred (will raise TemplateNotFound later)
    return preferred


@router.get("/", response_class=HTMLResponse)
async def list_jobs(request: Request, current_user = Depends(get_current_user_profile)):
    """Render the jobs list page."""
    return templates.TemplateResponse(
        request,
        "jobs/list.html",
        {"request": request, "current_user": current_user}
    )


@router.get("/create", response_class=HTMLResponse)
async def create_job_form(request: Request, current_user = Depends(get_current_user_profile)):
    """
    Render the job creation form (GET /jobs/create).
    This will prefer jobs/form.html if present, otherwise jobs/create.html.
    """
    template = _job_template("jobs/form.html", "jobs/create.html")
    return templates.TemplateResponse(
        request,
        template,
        {"request": request, "current_user": current_user}
    )


@router.post("/create")
async def create_job_submit(
    request: Request,
    title: str = Form(...),
    location: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    current_user = Depends(get_current_user_profile),
):
    """Handle simple job creation from the form and redirect back to jobs list.

    Note: this is a lightweight handler to keep routes and templates in sync.
    Integrate with the real JobService/DB logic as needed.
    """
    # TODO: integrate with real service (e.g., JobService(db).create(...))
    # For now, accept the form and redirect to the jobs list.
    try:
        # Basic validation example
        if not title.strip():
            raise ValueError("Title is required")
    except Exception as exc:
        template = _job_template("jobs/form.html", "jobs/create.html")
        return templates.TemplateResponse(
            request,
            template,
            {"request": request, "current_user": current_user, "error": str(exc), "title": title, "location": location, "description": description},
        )

    # On success redirect to jobs list (replace with created item's page if desired)
    return RedirectResponse(url="/jobs", status_code=302)
