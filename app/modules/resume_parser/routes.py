from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from typing import List, Optional
import uuid

from app.utils.enhanced_templates import EnhancedJinja2Templates
from app.dependencies import get_current_user_profile

router = APIRouter(prefix="/resume-parser", tags=["Resume Parser"])
templates = EnhancedJinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, current_user=Depends(get_current_user_profile)):
    """Render the resume parser home/index with stats and recent resumes."""
    # For now, no persistence: pass an empty list so templates that expect `resumes`
    # won't fail when rendering.
    resumes: List[dict] = []
    return templates.TemplateResponse(
        "resume_parser/index.html",
        {"request": request, "current_user": current_user, "resumes": resumes},
    )


@router.get("/list", response_class=HTMLResponse)
async def list_parsed(request: Request, current_user=Depends(get_current_user_profile)):
    """Render a list of recently parsed resumes (stubbed)."""
    resumes: List[dict] = []
    return templates.TemplateResponse(
        "resume_parser/list.html",
        {"request": request, "current_user": current_user, "resumes": resumes},
    )


@router.get("/{resume_id}", response_class=HTMLResponse)
async def view_resume(request: Request, resume_id: str, current_user=Depends(get_current_user_profile)):
    """Render a parsed resume detail view. Currently returns a placeholder if not found."""
    # As we don't have persistent storage yet, return a minimal placeholder
    # to avoid Jinja undefined errors. In the future this should load from DB.
    resume = {
        "id": resume_id,
        "first_name": "",
        "last_name": "",
        "title": None,
        "email": None,
        "phone": None,
        "location": None,
        "summary": None,
    }
    return templates.TemplateResponse(
        "resume_parser/view.html",
        {"request": request, "current_user": current_user, "resume": resume},
    )


@router.post("/parse", response_class=HTMLResponse)
async def parse_resume(request: Request, file: UploadFile = File(...), current_user=Depends(get_current_user_profile)):
    """Accept an uploaded resume file, "parse" it (stub), and render the result.

    This is a non-persistent, safe stub implementation that mimics parsing and
    returns a preview view. Replace with real parser + persistence when ready.
    """
    # Minimal safety: use filename to populate a few fields for the preview.
    filename = getattr(file, "filename", "") or "unknown"
    # Try to extract a name from filename (e.g., "john-doe.pdf")
    base = filename.rsplit(".", 1)[0]
    parts = base.replace("_", " ").replace("-", " ").split()
    first_name = parts[0].capitalize() if parts else "Candidate"
    last_name = parts[1].capitalize() if len(parts) > 1 else ""

    parsed_resume = {
        "id": str(uuid.uuid4()),
        "first_name": first_name,
        "last_name": last_name,
        "title": None,
        "email": None,
        "phone": None,
        "location": None,
        "summary": None,
    }

    # If the request is from HTMX, return a partial HTML fragment (a single resume card)
    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse(
            "resume_parser/partials/resume_row.html",
            {"request": request, "resume": parsed_resume},
        )

    # Default: render full detail view
    return templates.TemplateResponse(
        "resume_parser/view.html",
        {"request": request, "current_user": current_user, "resume": parsed_resume},
    )
