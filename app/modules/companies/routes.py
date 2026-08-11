
"""Companies module routes."""

import re
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import TemplateNotFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_profile
from app.modules.companies.models import Company
from app.modules.companies.repositories import CompanyRepository
from app.utils.enhanced_templates import EnhancedJinja2Templates
from app.utils.inspect_model import get_model_fields_sqlalchemy


router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)

templates = EnhancedJinja2Templates(
    directory="app/templates"
)


def _slugify(value: str) -> str:
    """
    Convert a company name/slug into a URL-friendly slug.

    Supports normal ASCII names. If the result is empty
    (for example, an Arabic-only company name), a unique
    fallback slug is generated.
    """
    value = (value or "").strip().lower()

    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value)

    slug = value.strip("-")

    if not slug:
        slug = f"company-{uuid4().hex[:8]}"

    return slug


def _get_form_values(form) -> dict:
    """Convert submitted form data into a normal dictionary."""
    return {
        key: value
        for key, value in form.items()
    }


def _is_checked(value) -> bool:
    """Convert common HTML checkbox values to bool."""
    return value in (
        "1",
        "true",
        "True",
        "on",
        "yes",
    )


# ---------------------------------------------------------------------------
# Companies list
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_class=HTMLResponse,
    name="companies:list",
)
async def list_companies(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Display all companies."""
    repo = CompanyRepository(db)

    companies = repo.get_all()

    fields = get_model_fields_sqlalchemy(Company)

    try:
        return templates.TemplateResponse(
            request,
            "companies/list.html",
            {
                "request": request,
                "companies": companies,
                "fields": fields,
                "current_user": current_user,
                "attribute": getattr,
            },
        )

    except TemplateNotFound:
        return {
            "message": "Companies list endpoint",
            "count": len(companies),
        }


# ---------------------------------------------------------------------------
# Create company - form
# ---------------------------------------------------------------------------

@router.get(
    "/create",
    response_class=HTMLResponse,
    name="companies:create_form",
)
async def create_company_form(
    request: Request,
    current_user=Depends(get_current_user_profile),
):
    """Display company creation form."""
    fields = get_model_fields_sqlalchemy(Company)

    return templates.TemplateResponse(
        request,
        "companies/form.html",
        {
            "request": request,
            "action": "create",
            "fields": fields,
            "current_user": current_user,
            "attribute": getattr,
        },
    )


# ---------------------------------------------------------------------------
# Create company - submit
# ---------------------------------------------------------------------------

@router.post(
    "/create",
)
async def create_company_submit(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Create a new company."""

    form = await request.form()

    # ---------------------------------------------------------
    # Read form values
    # ---------------------------------------------------------

    name = str(form.get("name") or "").strip()

    if not name:
        fields = get_model_fields_sqlalchemy(Company)

        return templates.TemplateResponse(
            request,
            "companies/form.html",
            {
                "request": request,
                "action": "create",
                "fields": fields,
                "error": "Company name is required.",
                "form_values": _get_form_values(form),
                "current_user": current_user,
                "attribute": getattr,
            },
            status_code=400,
        )

    submitted_slug = str(form.get("slug") or "").strip()

    slug = (
        _slugify(submitted_slug)
        if submitted_slug
        else _slugify(name)
    )

    description = str(
        form.get("description") or ""
    ).strip()

    timezone = str(
        form.get("timezone") or "UTC"
    ).strip()

    website = str(
        form.get("website") or ""
    ).strip()

    is_active = _is_checked(
        form.get("is_active")
    )

    # ---------------------------------------------------------
    # Build company data
    # ---------------------------------------------------------

    data = {
        "name": name,
        "slug": slug,
        "description": description or None,
        "timezone": timezone or "UTC",
        "website": website or None,
        "is_active": is_active,
    }

    repo = CompanyRepository(db)

    # ---------------------------------------------------------
    # Create company
    # ---------------------------------------------------------

    try:
        company = repo.create(data)

        # IMPORTANT:
        # Do NOT redirect to /companies/{slug} here.
        #
        # The company detail route currently has a template
        # rendering problem. After successful creation, go
        # directly back to the companies table.
        return RedirectResponse(
            url="/companies/",
            status_code=303,
        )

    except IntegrityError as exc:
        db.rollback()

        fields = get_model_fields_sqlalchemy(Company)

        error_message = str(exc).lower()

        if "slug" in error_message:
            error = "Company with this slug already exists."
        elif "name" in error_message:
            error = "A company with this name already exists."
        else:
            error = (
                "Unable to create the company. "
                "Please check the submitted data."
            )

        return templates.TemplateResponse(
            request,
            "companies/form.html",
            {
                "request": request,
                "action": "create",
                "fields": fields,
                "error": error,
                "form_values": _get_form_values(form),
                "current_user": current_user,
                "attribute": getattr,
            },
            status_code=400,
        )

    except Exception:
        db.rollback()

        fields = get_model_fields_sqlalchemy(Company)

        return templates.TemplateResponse(
            request,
            "companies/form.html",
            {
                "request": request,
                "action": "create",
                "fields": fields,
                "error": (
                    "An unexpected error occurred while "
                    "creating the company."
                ),
                "form_values": _get_form_values(form),
                "current_user": current_user,
                "attribute": getattr,
            },
            status_code=500,
        )


# ---------------------------------------------------------------------------
# Company detail
# ---------------------------------------------------------------------------

@router.get(
    "/{slug}",
    response_class=HTMLResponse,
    name="companies:detail",
)
async def company_detail(
    request: Request,
    slug: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Display company details."""

    repo = CompanyRepository(db)

    company = repo.get_by_slug(slug)

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    fields = get_model_fields_sqlalchemy(Company)

    return templates.TemplateResponse(
        request,
        "companies/detail.html",
        {
            "request": request,
            "company": company,
            "fields": fields,
            "current_user": current_user,
            "attribute": getattr,
        },
    )


# ---------------------------------------------------------------------------
# Edit company - form
# ---------------------------------------------------------------------------

@router.get(
    "/{slug}/edit",
    response_class=HTMLResponse,
    name="companies:edit_form",
)
async def edit_company_form(
    request: Request,
    slug: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Display company edit form."""

    repo = CompanyRepository(db)

    company = repo.get_by_slug(slug)

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    fields = get_model_fields_sqlalchemy(Company)

    return templates.TemplateResponse(
        request,
        "companies/form.html",
        {
            "request": request,
            "action": "edit",
            "company": company,
            "fields": fields,
            "current_user": current_user,
            "attribute": getattr,
        },
    )


# ---------------------------------------------------------------------------
# Edit company - submit
# ---------------------------------------------------------------------------

@router.post(
    "/{slug}/edit",
)
async def edit_company_submit(
    request: Request,
    slug: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Update an existing company."""

    form = await request.form()

    repo = CompanyRepository(db)

    company = repo.get_by_slug(slug)

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    # ---------------------------------------------------------
    # Read form values
    # ---------------------------------------------------------

    name = str(
        form.get("name") or company.name or ""
    ).strip()

    if not name:
        fields = get_model_fields_sqlalchemy(Company)

        return templates.TemplateResponse(
            request,
            "companies/form.html",
            {
                "request": request,
                "action": "edit",
                "company": company,
                "fields": fields,
                "error": "Company name is required.",
                "form_values": _get_form_values(form),
                "current_user": current_user,
                "attribute": getattr,
            },
            status_code=400,
        )

    submitted_slug = str(
        form.get("slug") or ""
    ).strip()

    if submitted_slug:
        new_slug = _slugify(submitted_slug)
    else:
        new_slug = company.slug or _slugify(name)

    description = str(
        form.get("description") or ""
    ).strip()

    timezone = str(
        form.get("timezone")
        or company.timezone
        or "UTC"
    ).strip()

    website = str(
        form.get("website") or ""
    ).strip()

    is_active = _is_checked(
        form.get("is_active")
    )

    # ---------------------------------------------------------
    # Build update data
    # ---------------------------------------------------------

    data = {
        "name": name,
        "slug": new_slug,
        "description": description or None,
        "timezone": timezone or "UTC",
        "website": website or None,
        "is_active": is_active,
    }

    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------

    try:
        updated = repo.update(
            company,
            data,
        )

        # After editing, return to companies table.
        # This avoids the currently broken detail template.
        return RedirectResponse(
            url="/companies/",
            status_code=303,
        )

    except IntegrityError as exc:
        db.rollback()

        fields = get_model_fields_sqlalchemy(Company)

        error_message = str(exc).lower()

        if "slug" in error_message:
            error = "Company with this slug already exists."
        elif "name" in error_message:
            error = "A company with this name already exists."
        else:
            error = (
                "Unable to update the company. "
                "Please check the submitted data."
            )

        return templates.TemplateResponse(
            request,
            "companies/form.html",
            {
                "request": request,
                "action": "edit",
                "company": company,
                "fields": fields,
                "error": error,
                "form_values": _get_form_values(form),
                "current_user": current_user,
                "attribute": getattr,
            },
            status_code=400,
        )

    except Exception:
        db.rollback()

        fields = get_model_fields_sqlalchemy(Company)

        return templates.TemplateResponse(
            request,
            "companies/form.html",
            {
                "request": request,
                "action": "edit",
                "company": company,
                "fields": fields,
                "error": (
                    "An unexpected error occurred while "
                    "updating the company."
                ),
                "form_values": _get_form_values(form),
                "current_user": current_user,
                "attribute": getattr,
            },
            status_code=500,
        )


# ---------------------------------------------------------------------------
# Delete company
# ---------------------------------------------------------------------------

@router.post(
    "/{slug}/delete",
)
async def delete_company(
    request: Request,
    slug: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Soft-delete a company."""

    repo = CompanyRepository(db)

    company = repo.get_by_slug(slug)

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    try:
        repo.soft_delete(company)

        return RedirectResponse(
            url="/companies/",
            status_code=303,
        )

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to delete company.",
        )
