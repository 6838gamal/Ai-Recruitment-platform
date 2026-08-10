"""Users module routes."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.database import get_db
from app.dependencies import get_current_user_profile, require_permission

# new: import inspection helper and UserProfile model to build dynamic fields
from app.utils.inspect_model import get_model_fields_sqlalchemy
from app.modules.users.models import UserProfile

router = APIRouter(prefix="/users", tags=["Users"])
templates = Jinja2Templates(directory="app/templates")


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
    # build dynamic fields metadata for UserProfile
    fields = get_model_fields_sqlalchemy(UserProfile)

    # Render template manually to avoid passing the full context dict into
    # Jinja2's get_template (some starlette/jinja2 versions pass the context
    # through to get_template leading to an unhashable dict inside the
    # template cache key).
    template = templates.env.get_template("users/list.html")
    content = template.render(
        request=request,
        users=users,
        total=total,
        page=page,
        current_user=current_user,
        fields=fields,
    )
    return HTMLResponse(content)


@router.get("/profile", response_class=HTMLResponse, name="users:profile")
async def my_profile(
    request: Request,
    current_user=Depends(get_current_user_profile),
):
    """Current user's profile page."""
    # Provide dynamic fields metadata to template so it can render gracefully
    fields = get_model_fields_sqlalchemy(UserProfile)

    template = templates.env.get_template("users/profile.html")
    content = template.render(
        request=request,
        profile=current_user,
        current_user=current_user,
        fields=fields,
    )
    return HTMLResponse(content)
