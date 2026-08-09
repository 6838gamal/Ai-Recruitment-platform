from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_permission
from app.core.permissions import Permission
from app.modules.accounts.services import AccountService
# models.py defines User not Account; import User and alias as Account for routes compatibility
from app.modules.accounts.models import User as Account
from app.utils.inspect_model import get_model_fields_sqlalchemy

router = APIRouter(prefix="/accounts", tags=["Accounts"]) 
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse, name="accounts:list")
async def accounts_list(request: Request, db: Session = Depends(get_db), current_user=Depends(require_permission(Permission.VIEW_ACCOUNTS))):
    service = AccountService(db)
    accounts = service.list_accounts()
    fields = get_model_fields_sqlalchemy(Account)
    return templates.TemplateResponse(request, "accounts/list.html", {"accounts": accounts, "fields": fields, "current_user": current_user})
