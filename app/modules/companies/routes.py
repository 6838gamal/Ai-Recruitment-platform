from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
import uuid
import logging

from jinja2 import TemplateError

from app.core.permissions import Permission
from app.database import get_db
from app.dependencies import require_permission
from app.utils.inspect_model import get_model_fields_sqlalchemy
from app.modules.companies.services import CompanyService
from app.modules.companies.models import Company

router = APIRouter(prefix="/companies", tags=["Companies"]) 
templates = Jinja2Templates(directory="app/templates")


def render_template(name: str, context: dict, status_code: Optional[int] = None):
    """Safe template renderer that prefers TemplateResponse but falls back to manual render on TypeError.

    Uses positional args for TemplateResponse to be compatible across starlette/jinja2 versions.
    """
    try:
        if status_code is not None:
            return templates.TemplateResponse(name, context, status_code=status_code)
        return templates.TemplateResponse(name, context)
    except TypeError as exc:
        logging.exception("TemplateResponse TypeError for %s: %s", name, exc)
        try:
            template = templates.env.get_template(name)
            rendered = template.render(**context)
            return HTMLResponse(rendered, status_code=status_code) if status_code is not None else HTMLResponse(rendered)
        except TemplateError:
            # Re-raise to surface the underlying problem if fallback fails
            raise


@router.get("/", response_class=HTMLResponse, name="companies:list")
async def company_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.VIEW_COMPANIES)),
):
    """List all companies."""
    service = CompanyService(db)
    companies = service.list_companies()
    fields = get_model_fields_sqlalchemy(Company)
    return render_template(
        name="companies/list.html",
        context={
            "request": request,
            "companies": companies,
            "fields": fields,
            "current_user": current_user,
        },
    )


@router.get("/create", response_class=HTMLResponse, name="companies:create")
async def company_create_get(
    request: Request, 
    db: Session = Depends(get_db), 
    current_user=Depends(require_permission(Permission.MANAGE_COMPANIES))
):
    """Render create company form."""
    fields = get_model_fields_sqlalchemy(Company)
    return render_template(
        name="companies/form.html",
        context={
            "request": request,
            "fields": fields, 
            "action": "create", 
            "current_user": current_user, 
            "error": None
        },
    )


@router.post("/create")
async def company_create_post(
    request: Request,
    db: Session = Depends(get_db), 
    current_user=Depends(require_permission(Permission.MANAGE_COMPANIES))
):
    """Create new company (dynamic form handling)."""
    service = CompanyService(db)

    form = await request.form()
    data = {}
    for k, v in form.items():
        # checkbox values set to '1' in template -> True
        if v == "1":
            data[k] = True
        else:
            data[k] = v.strip() if isinstance(v, str) else v

    try:
        company = service.create_company(data)
        db.commit()
    except IntegrityError:
        db.rollback()
        fields = get_model_fields_sqlalchemy(Company)
        return render_template(
            name="companies/form.html",
            context={
                "request": request,
                "fields": fields, 
                "action": "create", 
                "current_user": current_user, 
                "error": "Slug already exists or invalid data",
                "form_values": data,
            },
            status_code=400,
        )
    return RedirectResponse(url=f"/companies/{company.slug}", status_code=303)


@router.get("/{identifier}", response_class=HTMLResponse, name="companies:detail")
async def company_detail(
    request: Request, 
    identifier: str, 
    db: Session = Depends(get_db), 
    current_user=Depends(require_permission(Permission.VIEW_COMPANIES))
):
    """Get company detail."""
    service = CompanyService(db)
    # Try slug first, then UUID id
    company = service.get_by_slug(identifier)
    if not company:
        try:
            uid = uuid.UUID(identifier)
            company = service.get_by_id(uid)
        except (ValueError, TypeError):
            company = None
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    fields = get_model_fields_sqlalchemy(Company)
    return render_template(
        name="companies/detail.html",
        context={
            "request": request,
            "company": company, 
            "fields": fields, 
            "current_user": current_user
        },
    )


@router.get("/{identifier}/edit", response_class=HTMLResponse, name="companies:edit")
async def company_edit_get(
    request: Request, 
    identifier: str, 
    db: Session = Depends(get_db), 
    current_user=Depends(require_permission(Permission.MANAGE_COMPANIES))
):
    """Render edit company form."""
    service = CompanyService(db)
    # Try slug first, then UUID id
    company = service.get_by_slug(identifier)
    if not company:
        try:
            uid = uuid.UUID(identifier)
            company = service.get_by_id(uid)
        except (ValueError, TypeError):
            company = None
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    fields = get_model_fields_sqlalchemy(Company)
    return render_template(
        name="companies/form.html",
        context={
            "request": request,
            "company": company, 
            "fields": fields, 
            "action": "edit", 
            "current_user": current_user, 
            "error": None
        },
    )


@router.post("/{identifier}/edit")
async def company_edit_post(
    request: Request, 
    identifier: str, 
    db: Session = Depends(get_db), 
    current_user=Depends(require_permission(Permission.MANAGE_COMPANIES))
):
    """Update company (dynamic form handling)."""
    service = CompanyService(db)
    company = service.get_by_slug(identifier)
    if not company:
        try:
            uid = uuid.UUID(identifier)
            company = service.get_by_id(uid)
        except (ValueError, TypeError):
            company = None
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    form = await request.form()
    data = {}
    for k, v in form.items():
        if v == "1":
            data[k] = True
        else:
            data[k] = v.strip() if isinstance(v, str) else v

    try:
        updated = service.update_company(company, data)
        db.commit()
    except IntegrityError:
        db.rollback()
        fields = get_model_fields_sqlalchemy(Company)
        return render_template(
            name="companies/form.html",
            context={
                "request": request,
                "company": company, 
                "fields": fields, 
                "action": "edit", 
                "current_user": current_user, 
                "error": "Slug already exists or invalid data",
                "form_values": data,
            },
            status_code=400,
        )
    return RedirectResponse(url=f"/companies/{updated.slug}", status_code=303)


@router.post("/{identifier}/delete")
async def company_delete(
    request: Request,
    identifier: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_COMPANIES)),
):
    """Delete company (soft-delete)."""
    service = CompanyService(db)

    # Try slug first, then UUID id
    company = service.get_by_slug(identifier)
    if not company:
        try:
            uid = uuid.UUID(identifier)
            company = service.get_by_id(uid)
        except (ValueError, TypeError):
            company = None

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    try:
        service.delete_company(company)
        db.commit()
    except Exception as e:
        db.rollback()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
        raise HTTPException(status_code=500, detail="Failed to delete company")

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JSONResponse({"status": "ok"})
    return RedirectResponse(url="/companies", status_code=303)
