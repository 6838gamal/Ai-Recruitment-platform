
"""Resume Parser module routes."""

from datetime import datetime
from pathlib import Path
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_profile
from app.utils.enhanced_templates import EnhancedJinja2Templates

from app.modules.resume_parser.models import ParsedResume
from app.modules.resume_parser.services import ResumeParserService


router = APIRouter(
    prefix="/resume-parser",
    tags=["Resume Parser"],
)

templates = EnhancedJinja2Templates(
    directory="app/templates"
)


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

UPLOAD_DIR = BASE_DIR / "uploads" / "resumes"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
}

MAX_FILE_SIZE = 10 * 1024 * 1024


# ============================================================
# Helpers
# ============================================================

def validate_filename(filename: Optional[str]) -> str:
    """Validate uploaded resume filename."""

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Please select a resume file.",
        )

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file format. "
                "Supported formats: PDF, DOC, DOCX."
            ),
        )

    return extension


async def save_upload_file(
    file: UploadFile,
    destination: Path,
) -> int:
    """Save uploaded file and return its size."""

    total_size = 0

    try:
        with destination.open("wb") as output:

            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            "Resume file is too large. "
                            "Maximum size is 10MB."
                        ),
                    )

                output.write(chunk)

    except Exception:
        if destination.exists():
            destination.unlink()

        raise

    finally:
        await file.close()

    return total_size


# ============================================================
# Dashboard
# ============================================================

@router.get(
    "/",
    response_class=HTMLResponse,
)
async def index(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Display resume parser dashboard."""

    total_resumes = (
        db.query(ParsedResume).count()
    )

    processed_resumes = (
        db.query(ParsedResume)
        .filter(
            ParsedResume.status == "completed"
        )
        .count()
    )

    failed_resumes = (
        db.query(ParsedResume)
        .filter(
            ParsedResume.status == "failed"
        )
        .count()
    )

    recent_resumes = (
        db.query(ParsedResume)
        .order_by(
            ParsedResume.created_at.desc()
        )
        .limit(5)
        .all()
    )

    last_resume = (
        db.query(ParsedResume)
        .filter(
            ParsedResume.status == "completed"
        )
        .order_by(
            ParsedResume.parsed_at.desc()
        )
        .first()
    )

    parse_times = (
        db.query(ParsedResume.parse_time)
        .filter(
            ParsedResume.status == "completed",
            ParsedResume.parse_time.isnot(None),
        )
        .all()
    )

    parse_values = [
        row[0]
        for row in parse_times
        if row[0] is not None
    ]

    average_parse_time = (
        round(
            sum(parse_values) / len(parse_values),
            2,
        )
        if parse_values
        else 0
    )

    stats = {
        "total_resumes": total_resumes,
        "processed_resumes": processed_resumes,
        "failed_resumes": failed_resumes,
        "average_parse_time": average_parse_time,
    }

    return templates.TemplateResponse(
        "resume_parser/index.html",
        {
            "request": request,
            "current_user": current_user,
            "resumes": recent_resumes,
            "recent_resumes": recent_resumes,
            "last_resume": last_resume,
            "stats": stats,
        },
    )


# ============================================================
# Upload + Parse Resume
# ============================================================

@router.post(
    "/parse",
    response_class=HTMLResponse,
)
async def parse_resume(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Upload, parse and match a resume."""

    filename = file.filename or "resume"

    extension = validate_filename(filename)

    # --------------------------------------------------------
    # Generate unique stored filename
    # --------------------------------------------------------

    stored_filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

    destination = (
        UPLOAD_DIR / stored_filename
    )

    # --------------------------------------------------------
    # Save uploaded file
    # --------------------------------------------------------

    file_size = await save_upload_file(
        file=file,
        destination=destination,
    )

    # --------------------------------------------------------
    # Create database record
    # --------------------------------------------------------

    parsed_resume = ParsedResume(
        filename=filename,
        file_path=str(destination),
        file_type=extension.lstrip("."),
        file_size=file_size,
        status="processing",
        skills=[],
        experience=[],
        education=[],
        certifications=[],
        languages=[],
        matches=[],
        best_match_score=0.0,
    )

    db.add(parsed_resume)
    db.commit()
    db.refresh(parsed_resume)

    # --------------------------------------------------------
    # Parse resume
    # --------------------------------------------------------

    try:
        parser = ResumeParserService(
            db=db
        )

        result = parser.parse_and_match(
            file_path=destination,
            filename=filename,
            limit=20,
        )

        # ----------------------------------------------------
        # Personal information
        # ----------------------------------------------------

        parsed_resume.first_name = (
            result.get("first_name")
        )

        parsed_resume.last_name = (
            result.get("last_name")
        )

        parsed_resume.email = (
            result.get("email")
        )

        parsed_resume.phone = (
            result.get("phone")
        )

        parsed_resume.location = (
            result.get("location")
        )

        parsed_resume.title = (
            result.get("title")
        )

        parsed_resume.summary = (
            result.get("summary")
        )

        # ----------------------------------------------------
        # Extracted data
        # ----------------------------------------------------

        parsed_resume.skills = (
            result.get("skills", [])
        )

        parsed_resume.experience = (
            result.get("experience", [])
        )

        parsed_resume.education = (
            result.get("education", [])
        )

        parsed_resume.years_of_experience = (
            result.get(
                "years_of_experience",
                0,
            )
        )

        parsed_resume.resume_text = (
            result.get("resume_text")
        )

        # ----------------------------------------------------
        # Matching
        # ----------------------------------------------------

        parsed_resume.matches = (
            result.get("matches", [])
        )

        parsed_resume.best_match_score = (
            result.get(
                "best_match_score",
                0,
            )
        )

        # ----------------------------------------------------
        # Parsing information
        # ----------------------------------------------------

        parsed_resume.parse_time = (
            result.get("parse_time")
        )

        parsed_resume.status = "completed"

        parsed_resume.parsed_at = datetime.utcnow()

        db.add(parsed_resume)
        db.commit()
        db.refresh(parsed_resume)

    except Exception as exc:

        parsed_resume.status = "failed"

        parsed_resume.error_message = str(exc)[:4000]

        db.add(parsed_resume)
        db.commit()

        raise HTTPException(
            status_code=500,
            detail=(
                "Resume parsing failed: "
                f"{exc}"
            ),
        ) from exc

    # --------------------------------------------------------
    # Go directly to results page
    # --------------------------------------------------------

    return RedirectResponse(
        url=f"/resume-parser/{parsed_resume.id}",
        status_code=303,
    )


# ============================================================
# Parsed Resume List
# ============================================================

@router.get(
    "/list",
    response_class=HTMLResponse,
)
async def list_parsed(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Display all parsed resumes."""

    resumes = (
        db.query(ParsedResume)
        .order_by(
            ParsedResume.created_at.desc()
        )
        .all()
    )

    return templates.TemplateResponse(
        "resume_parser/list.html",
        {
            "request": request,
            "current_user": current_user,
            "resumes": resumes,
        },
    )


# ============================================================
# Resume Details + Matching Results
# ============================================================

@router.get(
    "/{resume_id}",
    response_class=HTMLResponse,
)
async def view_resume(
    request: Request,
    resume_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Display parsed resume and candidate matches."""

    resume = (
        db.query(ParsedResume)
        .filter(
            ParsedResume.id == resume_id
        )
        .first()
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    return templates.TemplateResponse(
        "resume_parser/view.html",
        {
            "request": request,
            "current_user": current_user,
            "resume": resume,
            "matches": resume.matches or [],
        },
    )


# ============================================================
# Delete Parsed Resume
# ============================================================

@router.post(
    "/{resume_id}/delete",
)
async def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Delete parsed resume and uploaded file."""

    resume = (
        db.query(ParsedResume)
        .filter(
            ParsedResume.id == resume_id
        )
        .first()
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    # --------------------------------------------------------
    # Delete physical file
    # --------------------------------------------------------

    if resume.file_path:

        try:
            file_path = Path(
                resume.file_path
            )

            if file_path.exists():
                file_path.unlink()

        except OSError:
            pass

    # --------------------------------------------------------
    # Delete database record
    # --------------------------------------------------------

    db.delete(resume)
    db.commit()

    return RedirectResponse(
        url="/resume-parser/",
        status_code=303,
    )

