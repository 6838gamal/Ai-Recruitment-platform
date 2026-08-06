"""Resume Parser module routes."""
from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.core.permissions import Permission
from app.dependencies import require_permission
from app.modules.resume_parser.services import ResumeParserService

router = APIRouter(prefix="/resume-parser", tags=["Resume Parser"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="resume_parser:index")
async def parser_index(
    request: Request,
    current_user=Depends(require_permission(Permission.MANAGE_CANDIDATES)),
):
    return templates.TemplateResponse("resume_parser/index.html", {
        "request": request, "current_user": current_user
    })


@router.post("/upload", name="resume_parser:upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user=Depends(require_permission(Permission.MANAGE_CANDIDATES)),
):
    """Upload and parse a resume file."""
    file_bytes = await file.read()
    service = ResumeParserService()

    content_type = file.content_type or ""
    filename = file.filename or ""

    if "pdf" in content_type or filename.endswith(".pdf"):
        result = service.parse_pdf(file_bytes)
    elif "word" in content_type or "docx" in content_type or filename.endswith(".docx"):
        result = service.parse_docx(file_bytes)
    else:
        result = service.parse_pdf(file_bytes)  # try pdf as fallback

    return JSONResponse(content=result.model_dump())
