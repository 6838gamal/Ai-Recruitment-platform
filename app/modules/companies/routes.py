from app.utils.inspect_model import get_model_fields_sqlalchemy
from app.modules.companies.models import Company

# Update the company_list route to fetch companies and pass fields
# We'll keep the existing permission logic and add dynamic fields

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.database import get_db
from app.dependencies import require_permission
from app.modules.companies.services import CompanyService

router = APIRouter(prefix="/companies", tags=["Companies"]) 
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="companies:list")
async def company_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.VIEW_COMPANIES)),
):
    service = CompanyService(db)
    companies = service.list_companies()  # returns list of Company objects
    fields = get_model_fields_sqlalchemy(Company)
    return templates.TemplateResponse(request, "companies/list.html", {
        "current_user": current_user,
        "companies": companies,
        "fields": fields,
    })
