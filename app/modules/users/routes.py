"""Users module routes."""

from urllib.parse import quote_plus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from jinja2 import TemplateNotFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_profile
from app.modules.jobs.models import JobPosting
from app.modules.users.models import UserProfile
from app.modules.users.repositories import UserProfileRepository
from app.utils.enhanced_templates import EnhancedJinja2Templates
from app.utils.inspect_model import get_model_fields_sqlalchemy


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

templates = EnhancedJinja2Templates(
    directory="app/templates"
)


# ============================================================
# HELPERS
# ============================================================

def get_companies(db: Session):
    """Return all active companies."""

    try:
        from app.modules.companies.models import Company

        return (
            db.query(Company)
            .filter(
                Company.deleted_at.is_(None)
            )
            .order_by(Company.name.asc())
            .all()
        )

    except Exception:
        return []


def render_job_create(
    request: Request,
    current_user,
    db: Session,
    error: str | None = None,
    form_values=None,
    status_code: int = 200,
):
    """Render the job creation form."""

    return templates.TemplateResponse(
        request,
        "jobs/create.html",
        {
            "request": request,
            "current_user": current_user,
            "companies": get_companies(db),
            "error": error,
            "form_values": form_values,
        },
        status_code=status_code,
    )


# ============================================================
# USERS
# ============================================================

@router.get(
    "/",
    response_class=HTMLResponse,
    name="users:list",
)
async def list_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """List users."""

    repo = UserProfileRepository(db)

    users = []

    try:
        if current_user and current_user.company_id:
            users = repo.get_by_company(
                current_user.company_id
            )
        else:
            users = repo.get_all()

    except Exception:
        users = []

    fields = get_model_fields_sqlalchemy(
        UserProfile
    )

    try:
        return templates.TemplateResponse(
            request,
            "users/list.html",
            {
                "request": request,
                "users": users,
                "fields": fields,
                "current_user": current_user,
                "attribute": getattr,
            },
        )

    except TemplateNotFound:
        return JSONResponse(
            {
                "message": "Users list endpoint",
                "count": len(users),
            }
        )


@router.get(
    "/create",
    response_class=HTMLResponse,
    name="users:create_form",
)
async def create_user_form(
    request: Request,
    current_user=Depends(get_current_user_profile),
):
    """Display user creation form."""

    fields = get_model_fields_sqlalchemy(
        UserProfile
    )

    return templates.TemplateResponse(
        request,
        "users/form.html",
        {
            "request": request,
            "action": "create",
            "fields": fields,
            "current_user": current_user,
            "attribute": getattr,
        },
    )


@router.post("/create")
async def create_user_submit(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Create a user profile."""

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="You must be logged in.",
        )

    form = await request.form()

    # --------------------------------------------------------
    # IMPORTANT:
    # Never trust user_id from the HTML form.
    #
    # The authenticated user's ID is the only trusted value.
    # --------------------------------------------------------

    authenticated_user_id = getattr(
        current_user,
        "user_id",
        None,
    )

    if not authenticated_user_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "Current user profile is missing user_id."
            ),
        )

    data = {
        "user_id": authenticated_user_id,
        "company_id": current_user.company_id,
        "role": form.get("role") or "user",
        "first_name": form.get("first_name"),
        "last_name": form.get("last_name"),
        "phone": form.get("phone"),
        "avatar_url": None,
        "job_title": form.get("job_title"),
        "department": form.get("department"),
    }

    repo = UserProfileRepository(db)

    try:
        profile = repo.create(data)

        return RedirectResponse(
            url=f"/users/{quote_plus(str(profile.id))}",
            status_code=303,
        )

    except IntegrityError as exc:
        db.rollback()

        fields = get_model_fields_sqlalchemy(
            UserProfile
        )

        error = (
            str(exc.orig)
            if exc.orig
            else str(exc)
        )

        return templates.TemplateResponse(
            request,
            "users/form.html",
            {
                "request": request,
                "action": "create",
                "fields": fields,
                "error": error,
                "form_values": form,
                "current_user": current_user,
                "attribute": getattr,
            },
            status_code=400,
        )


@router.get(
    "/{id}",
    response_class=HTMLResponse,
    name="users:detail",
)
async def user_detail(
    request: Request,
    id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Display user details."""

    repo = UserProfileRepository(db)

    profile = repo.get(id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    fields = get_model_fields_sqlalchemy(
        UserProfile
    )

    return templates.TemplateResponse(
        request,
        "users/detail.html",
        {
            "request": request,
            "user": profile,
            "fields": fields,
            "current_user": current_user,
            "attribute": getattr,
        },
    )


@router.get(
    "/{id}/edit",
    response_class=HTMLResponse,
    name="users:edit_form",
)
async def edit_user_form(
    request: Request,
    id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Display user edit form."""

    repo = UserProfileRepository(db)

    profile = repo.get(id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    fields = get_model_fields_sqlalchemy(
        UserProfile
    )

    return templates.TemplateResponse(
        request,
        "users/form.html",
        {
            "request": request,
            "action": "edit",
            "user": profile,
            "fields": fields,
            "current_user": current_user,
            "attribute": getattr,
        },
    )


@router.post("/{id}/edit")
async def edit_user_submit(
    request: Request,
    id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Update user profile."""

    form = await request.form()

    repo = UserProfileRepository(db)

    profile = repo.get(id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    data = {
        "first_name": (
            form.get("first_name")
            or profile.first_name
        ),
        "last_name": (
            form.get("last_name")
            or profile.last_name
        ),
        "phone": (
            form.get("phone")
            or profile.phone
        ),
        "job_title": (
            form.get("job_title")
            or profile.job_title
        ),
        "department": (
            form.get("department")
            or profile.department
        ),
        "role": (
            form.get("role")
            or profile.role
        ),
    }

    try:
        updated = repo.update(
            profile,
            data,
        )

        return RedirectResponse(
            url=f"/users/{quote_plus(str(updated.id))}",
            status_code=303,
        )

    except IntegrityError as exc:
        db.rollback()

        fields = get_model_fields_sqlalchemy(
            UserProfile
        )

        error = (
            str(exc.orig)
            if exc.orig
            else str(exc)
        )

        return templates.TemplateResponse(
            request,
            "users/form.html",
            {
                "request": request,
                "action": "edit",
                "user": profile,
                "fields": fields,
                "error": error,
                "form_values": form,
                "current_user": current_user,
                "attribute": getattr,
            },
            status_code=400,
        )


@router.post("/{id}/delete")
async def delete_user(
    request: Request,
    id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Soft delete user."""

    repo = UserProfileRepository(db)

    profile = repo.get(id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    repo.soft_delete(profile)

    return RedirectResponse(
        url="/users/",
        status_code=303,
    )


# ============================================================
# JOBS
# ============================================================

@router.get(
    "/jobs/create",
    response_class=HTMLResponse,
    name="jobs:create_form",
)
async def create_job_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Display create job form."""

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail=(
                "You must be logged in "
                "to create a job."
            ),
        )

    # --------------------------------------------------------
    # Verify authenticated profile
    # --------------------------------------------------------

    created_by_id = getattr(
        current_user,
        "user_id",
        None,
    )

    if not created_by_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "Authenticated user profile "
                "does not contain user_id."
            ),
        )

    return templates.TemplateResponse(
        request,
        "jobs/create.html",
        {
            "request": request,
            "current_user": current_user,
            "companies": get_companies(db),
        },
    )


@router.post("/jobs/create")
async def create_job_submit(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Create a new job posting."""

    # ========================================================
    # 1. AUTHENTICATION
    # ========================================================

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail=(
                "You must be logged in "
                "to create a job."
            ),
        )

    # ========================================================
    # 2. GET USER ID FROM AUTHENTICATED PROFILE
    # ========================================================

    created_by_id = getattr(
        current_user,
        "user_id",
        None,
    )

    if created_by_id is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unable to determine the authenticated "
                "user ID. UserProfile.user_id is NULL."
            ),
        )

    # --------------------------------------------------------
    # Convert to UUID
    # --------------------------------------------------------

    try:
        created_by_id = UUID(
            str(created_by_id)
        )

    except (ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=400,
            detail=(
                "The authenticated user's ID "
                "is not a valid UUID."
            ),
        )

    # ========================================================
    # 3. VERIFY USER PROFILE
    # ========================================================

    profile = (
        db.query(UserProfile)
        .filter(
            UserProfile.user_id == created_by_id,
            UserProfile.deleted_at.is_(None),
        )
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=401,
            detail=(
                "The authenticated user does not have "
                "a valid active UserProfile."
            ),
        )

    # ========================================================
    # 4. READ FORM
    # ========================================================

    form = await request.form()

    title = (
        form.get("title")
        or ""
    ).strip()

    description = (
        form.get("description")
        or ""
    ).strip()

    location = (
        form.get("location")
        or ""
    ).strip()

    status = (
        form.get("status")
        or "draft"
    ).strip()

    company_id = (
        form.get("company_id")
        or ""
    ).strip()

    # ========================================================
    # 5. VALIDATE TITLE
    # ========================================================

    if not title:
        return render_job_create(
            request=request,
            current_user=current_user,
            db=db,
            error="Job title is required.",
            form_values=form,
            status_code=400,
        )

    # ========================================================
    # 6. COMPANY
    # ========================================================

    if not company_id:
        company_id = getattr(
            profile,
            "company_id",
            None,
        )

    if company_id == "":
        company_id = None

    # --------------------------------------------------------
    # Convert company ID to UUID if provided
    # --------------------------------------------------------

    if company_id:

        try:
            company_id = UUID(
                str(company_id)
            )

        except (
            ValueError,
            TypeError,
            AttributeError,
        ):
            return render_job_create(
                request=request,
                current_user=current_user,
                db=db,
                error="Invalid company ID.",
                form_values=form,
                status_code=400,
            )

    # ========================================================
    # 7. CREATE JOB
    # ========================================================

    job = JobPosting(
        title=title,
        description=description or None,
        location=location or None,
        status=status,
        company_id=company_id,
        created_by_id=created_by_id,
    )

    # ========================================================
    # 8. SAVE
    # ========================================================

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

        return render_job_create(
            request=request,
            current_user=current_user,
            db=db,
            error=error,
            form_values=form,
            status_code=400,
        )

    except Exception:
        db.rollback()
        raise

    # ========================================================
    # 9. SUCCESS
    # ========================================================

    return RedirectResponse(
        url="/jobs/",
        status_code=303,
    )
