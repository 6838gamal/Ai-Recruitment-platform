"""Users module routes."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.database import get_db
from app.dependencies import get_current_user_profile, require_permission

from app.utils.inspect_model import get_model_fields_sqlalchemy
from app.modules.users.models import UserProfile

# استيراد المصنع الآمن والدالة المعقمة
from app.utils.safe_jinja import templates
from app.utils.template_utils import sanitize_context

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_class=HTMLResponse, name="users:list")
async def user_list(
    request: Request,
    page: int = 1,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.VIEW_USERS)),
):
    """User list page."""
    from app.modules.users.services import UserService
    service = UserService(db)
    users, total = service.list_users(
        company_id=current_user.company_id,
        page=page,
        per_page=25,
    )
    fields = get_model_fields_sqlalchemy(UserProfile)

    context = {
        "request": request,
        "users": users,
        "total": total,
        "page": page,
        "current_user": current_user,
        "fields": fields,
    }
    # Pass `request` as the first argument to TemplateResponse
    return templates.TemplateResponse(request, "users/list.html", sanitize_context(context))


@router.get("/profile", response_class=HTMLResponse, name="users:profile")
async def my_profile(
    request: Request,
    current_user=Depends(get_current_user_profile),
):
    """Current user's profile page."""
    fields = get_model_fields_sqlalchemy(UserProfile)
    context = {
        "request": request,
        "profile": current_user,
        "current_user": current_user,
        "fields": fields,
    }
    # Pass `request` as the first argument to TemplateResponse
    return templates.TemplateResponse(request, "users/profile.html", sanitize_context(context))
