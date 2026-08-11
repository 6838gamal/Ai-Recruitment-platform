from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from jinja2 import TemplateNotFound

from app.database import get_db
from app.utils.enhanced_templates import EnhancedJinja2Templates
from app.modules.companies.repositories import CompanyRepository
from app.modules.companies.models import Company
from app.utils.inspect_model import get_model_fields_sqlalchemy
from app.dependencies import get_current_user_profile

router = APIRouter(prefix="/companies", tags=["Companies"]) 
templates = EnhancedJinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="companies:list")
async def list_companies(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user_profile)):
    """Render the companies list page using the dynamic table partial.

    Falls back to a simple JSON response if the template is not available so
    existing API behavior is preserved.
    """
    repo = CompanyRepository(db)
    companies = repo.get_all()
    fields = get_model_fields_sqlalchemy(Company)

    try:
        return templates.TemplateResponse(
            request,
            "companies/list.html",
            {"request": request, "companies": companies, "fields": fields, "current_user": current_user},
        )
    except TemplateNotFound:
        # Preserve original fallback behavior for environments without templates
        return {"message": "Companies list endpoint", "count": len(companies)}
