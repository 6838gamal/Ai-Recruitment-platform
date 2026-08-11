from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from jinja2 import TemplateNotFound
from urllib.parse import quote_plus
import re

from app.database import get_db
from app.utils.enhanced_templates import EnhancedJinja2Templates
from app.modules.companies.repositories import CompanyRepository
from app.modules.companies.models import Company
from app.utils.inspect_model import get_model_fields_sqlalchemy
from app.dependencies import get_current_user_profile

router = APIRouter(prefix="/companies", tags=["Companies"]) 
templates = EnhancedJinja2Templates(directory="app/templates")


def _slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


@router.get("/", response_class=HTMLResponse, name="companies:list")
async def list_companies(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user_profile)):
    repo = CompanyRepository(db)
    companies = repo.get_all()
    fields = get_model_fields_sqlalchemy(Company)

    try:
        return templates.TemplateResponse(
            request,
            "companies/list.html",
            {"request": request, "companies": companies, "fields": fields, "current_user": current_user, "attribute": getattr},
        )
    except TemplateNotFound:
        return {"message": "Companies list endpoint", "count": len(companies)}


@router.get("/create", response_class=HTMLResponse, name="companies:create_form")
async def create_company_form(request: Request, current_user=Depends(get_current_user_profile)):
    fields = get_model_fields_sqlalchemy(Company)
    return templates.TemplateResponse(
        request,
        "companies/form.html",
        {"request": request, "action": "create", "fields": fields, "current_user": current_user, "attribute": getattr},
    )


@router.post("/create")
async def create_company_submit(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user_profile)):
    form = await request.form()
    name = form.get("name") or ""
    slug = form.get("slug") or _slugify(name)
    description = form.get("description")
    timezone = form.get("timezone") or "UTC"
    website = form.get("website")
    is_active = True if form.get("is_active") in ("1", "true", "on", "yes") else False

    data = {
        "name": name,
        "slug": slug,
        "description": description,
        "timezone": timezone,
        "website": website,
        "is_active": is_active,
    }

    repo = CompanyRepository(db)
    try:
        company = repo.create(data)
        return RedirectResponse(url=f"/companies/{quote_plus(company.slug)}", status_code=302)
    except IntegrityError as exc:
        db.rollback()
        fields = get_model_fields_sqlalchemy(Company)
        error = "Company with this slug already exists." if "slug" in str(exc).lower() else str(exc)
        return templates.TemplateResponse(
            request,
            "companies/form.html",
            {"request": request, "action": "create", "fields": fields, "error": error, "form_values": form, "current_user": current_user, "attribute": getattr},
        )


@router.get("/{slug}", response_class=HTMLResponse, name="companies:detail")
async def company_detail(request: Request, slug: str, db: Session = Depends(get_db), current_user=Depends(get_current_user_profile)):
    repo = CompanyRepository(db)
    company = repo.get_by_slug(slug)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    fields = get_model_fields_sqlalchemy(Company)
    return templates.TemplateResponse(
        request,
        "companies/detail.html",
        {"request": request, "company": company, "fields": fields, "current_user": current_user, "attribute": getattr},
    )


@router.get("/{slug}/edit", response_class=HTMLResponse, name="companies:edit_form")
async def edit_company_form(request: Request, slug: str, db: Session = Depends(get_db), current_user=Depends(get_current_user_profile)):
    repo = CompanyRepository(db)
    company = repo.get_by_slug(slug)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    fields = get_model_fields_sqlalchemy(Company)
    return templates.TemplateResponse(
        request,
        "companies/form.html",
        {"request": request, "action": "edit", "company": company, "fields": fields, "current_user": current_user, "attribute": getattr},
    )


@router.post("/{slug}/edit")
async def edit_company_submit(request: Request, slug: str, db: Session = Depends(get_db), current_user=Depends(get_current_user_profile)):
    form = await request.form()
    repo = CompanyRepository(db)
    company = repo.get_by_slug(slug)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    name = form.get("name") or company.name
    new_slug = form.get("slug") or _slugify(name) or company.slug
    description = form.get("description")
    timezone = form.get("timezone") or company.timezone
    website = form.get("website")
    is_active = True if form.get("is_active") in ("1", "true", "on", "yes") else False

    data = {
        "name": name,
        "slug": new_slug,
        "description": description,
        "timezone": timezone,
        "website": website,
        "is_active": is_active,
    }

    try:
        updated = repo.update(company, data)
        return RedirectResponse(url=f"/companies/{quote_plus(updated.slug)}", status_code=302)
    except IntegrityError as exc:
        db.rollback()
        fields = get_model_fields_sqlalchemy(Company)
        error = "Company with this slug already exists." if "slug" in str(exc).lower() else str(exc)
        return templates.TemplateResponse(
            request,
            "companies/form.html",
            {"request": request, "action": "edit", "company": company, "fields": fields, "error": error, "form_values": form, "current_user": current_user, "attribute": getattr},
        )


@router.post("/{slug}/delete")
async def delete_company(request: Request, slug: str, db: Session = Depends(get_db), current_user=Depends(get_current_user_profile)):
    repo = CompanyRepository(db)
    company = repo.get_by_slug(slug)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    repo.soft_delete(company)
    return RedirectResponse(url="/companies/", status_code=302)
