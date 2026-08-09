from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional

from app.core.permissions import Permission
from app.database import get_db
from app.dependencies import require_permission
from app.utils.inspect_model import get_model_fields_sqlalchemy
from app.modules.companies.services import CompanyService
from app.modules.companies.models import Company

router = APIRouter(prefix="/companies", tags=["Companies"]) 
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="companies:list")
async def company_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.VIEW_COMPANIES)),
):
    service = CompanyService(db)
    companies = service.list_companies()
    fields = get_model_fields_sqlalchemy(Company)
    return templates.TemplateResponse(request, "companies/list.html", {
        "current_user": current_user,
        "companies": companies,
        "fields": fields,
    })


@router.get("/create", response_class=HTMLResponse, name="companies:create")
async def company_create_get(request: Request, db: Session = Depends(get_db), current_user=Depends(require_permission(Permission.MANAGE_COMPANIES))):
    # render create form
    fields = get_model_fields_sqlalchemy(Company)
    return templates.TemplateResponse(request, "companies/form.html", {"request": request, "fields": fields, "action": "create", "current_user": current_user, "error": None})


@router.post("/create")
async def company_create_post(request: Request, name: str = Form(...), slug: str = Form(...), db: Session = Depends(get_db), current_user=Depends(require_permission(Permission.MANAGE_COMPANIES))):
    service = CompanyService(db)
    data = {"name": name.strip(), "slug": slug.strip()}
    try:
        company = service.create_company(data)
        db.commit()
    except IntegrityError:
        db.rollback()
        fields = get_model_fields_sqlalchemy(Company)
        return templates.TemplateResponse(request, "companies/form.html", {"request": request, "fields": fields, "action": "create", "current_user": current_user, "error": "Slug already exists or invalid data"})
    return RedirectResponse(url=f"/companies/{company.slug}", status_code=303)


@router.get("/{identifier}", response_class=HTMLResponse, name="companies:detail")
async def company_detail(request: Request, identifier: str, db: Session = Depends(get_db), current_user=Depends(require_permission(Permission.VIEW_COMPANIES))):
    service = CompanyService(db)
    # Try slug first, then UUID id
    company = service.get_by_slug(identifier)
    if not company:
        try:
            import uuid
            uid = uuid.UUID(identifier)
            company = service.get_by_id(uid)
        except Exception:
            company = None
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    fields = get_model_fields_sqlalchemy(Company)
    return templates.TemplateResponse(request, "companies/detail.html", {"request": request, "company": company, "fields": fields, "current_user": current_user})


@router.get("/{identifier}/edit", response_class=HTMLResponse, name="companies:edit")
async def company_edit_get(request: Request, identifier: str, db: Session = Depends(get_db), current_user=Depends(require_permission(Permission.MANAGE_COMPANIES))):
    service = CompanyService(db)
    # Try slug first, then UUID id
    company = service.get_by_slug(identifier)
    if not company:
        try:
            import uuid
            uid = uuid.UUID(identifier)
            company = service.get_by_id(uid)
        except Exception:
            company = None
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    fields = get_model_fields_sqlalchemy(Company)
    return templates.TemplateResponse(request, "companies/form.html", {"request": request, "company": company, "fields": fields, "action": "edit", "current_user": current_user, "error": None})


@router.post("/{identifier}/edit")
async def company_edit_post(request: Request, identifier: str, name: str = Form(...), slug: str = Form(...), db: Session = Depends(get_db), current_user=Depends(require_permission(Permission.MANAGE_COMPANIES))):
    service = CompanyService(db)
    company = service.get_by_slug(identifier)
    if not company:
        try:
            import uuid
            uid = uuid.UUID(identifier)
            company = service.get_by_id(uid)
        except Exception:
            company = None
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    data = {"name": name.strip(), "slug": slug.strip()}
    try:
        updated = service.update_company(company, data)
        db.commit()
    except IntegrityError:
        db.rollback()
        fields = get_model_fields_sqlalchemy(Company)
        return templates.TemplateResponse(request, "companies/form.html", {"request": request, "company": company, "fields": fields, "action": "edit", "current_user": current_user, "error": "Slug already exists or invalid data"})
    return RedirectResponse(url=f"/companies/{updated.slug}", status_code=303)
