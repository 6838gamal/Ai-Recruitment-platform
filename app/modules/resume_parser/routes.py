"""Resume Parser module routes."""
from fastapi import APIRouter, Depends, File, Request, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.core.permissions import Permission
from app.database import get_db
from app.dependencies import require_permission
from app.utils.inspect_model import get_model_fields_sqlalchemy
from app.utils.safe_jinja import templates
from app.utils.template_utils import sanitize_context
from app.modules.resume_parser.services import ResumeParserService
from app.modules.candidates.models import Candidate

router = APIRouter(prefix="/resume-parser", tags=["Resume Parser"])


@router.get("/", response_class=HTMLResponse, name="resume_parser:index")
async def parser_index(
    request: Request,
    page: int = 1,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_CANDIDATES)),
):
    """Resume parser main page with upload and history."""
    service = ResumeParserService(db)
    company_id = current_user.company_id
    
    # Get parsed resumes
    resumes, total = service.get_parsed_resumes(
        company_id=company_id,
        page=page,
        per_page=10
    )

    context = {
        "request": request,
        "current_user": current_user,
        "resumes": resumes,
        "total": total,
        "page": page,
    }
    
    return templates.TemplateResponse(
        request=request,
        name="resume_parser/index.html",
        context=sanitize_context(context),
    )


@router.post("/upload", name="resume_parser:upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_CANDIDATES)),
):
    """Upload and parse a resume file."""
    file_bytes = await file.read()
    service = ResumeParserService(db)

    content_type = file.content_type or ""
    filename = file.filename or ""

    if "pdf" in content_type or filename.endswith(".pdf"):
        result = service.parse_pdf(file_bytes)
    elif "word" in content_type or "docx" in content_type or filename.endswith(".docx"):
        result = service.parse_docx(file_bytes)
    else:
        result = service.parse_pdf(file_bytes)  # try pdf as fallback

    return JSONResponse(content=result.model_dump())


@router.get("/{resume_id}", response_class=HTMLResponse, name="resume_parser:view")
async def view_parsed_resume(
    request: Request,
    resume_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.VIEW_CANDIDATES)),
):
    """View a parsed resume detail."""
    service = ResumeParserService(db)
    
    try:
        resume_uuid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid resume ID")
    
    resume = service.get_parsed_resume_by_id(resume_uuid, current_user.company_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    fields = get_model_fields_sqlalchemy(Candidate)

    context = {
        "request": request,
        "resume": resume,
        "current_user": current_user,
        "fields": fields,
    }
    
    return templates.TemplateResponse(
        request=request,
        name="resume_parser/view.html",
        context=sanitize_context(context),
    )


@router.get("/{resume_id}/edit", response_class=HTMLResponse, name="resume_parser:edit")
async def edit_parsed_resume(
    request: Request,
    resume_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_CANDIDATES)),
):
    """Edit a parsed resume information."""
    service = ResumeParserService(db)
    
    try:
        resume_uuid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid resume ID")
    
    resume = service.get_parsed_resume_by_id(resume_uuid, current_user.company_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    fields = get_model_fields_sqlalchemy(Candidate)

    context = {
        "request": request,
        "resume": resume,
        "current_user": current_user,
        "fields": fields,
        "action": "edit",
    }
    
    return templates.TemplateResponse(
        request=request,
        name="resume_parser/form.html",
        context=sanitize_context(context),
    )
