"""Users module routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.permissions import Permission
from app.database import get_db
from app.dependencies import (
    get_current_user_profile,
    require_permission,
)
from app.utils.inspect_model import get_model_fields_sqlalchemy
from app.modules.users.models import UserProfile
from app.utils.safe_jinja import templates
from app.utils.template_utils import sanitize_context


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_class=HTMLResponse,
    name="users:list",
)
async def user_list(
    request: Request,
    page: int = 1,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(Permission.VIEW_USERS)
    ),
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

    return templates.TemplateResponse(
        request=request,
        name="users/list.html",
        context=sanitize_context(context),
    )


@router.get(
    "/{user_id}",
    response_class=HTMLResponse,
    name="users:view",
)
async def user_view(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(Permission.VIEW_USERS)
    ),
):
    """User detail view page."""

    from app.modules.users.services import UserService

    service = UserService(db)

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid user ID")

    user = db.query(UserProfile).filter(
        UserProfile.id == user_uuid,
        UserProfile.company_id == current_user.company_id,
        UserProfile.deleted_at.is_(None),
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    fields = get_model_fields_sqlalchemy(UserProfile)

    context = {
        "request": request,
        "user": user,
        "current_user": current_user,
        "fields": fields,
    }

    return templates.TemplateResponse(
        request=request,
        name="users/view.html",
        context=sanitize_context(context),
    )


@router.get(
    "/{user_id}/edit",
    response_class=HTMLResponse,
    name="users:edit",
)
async def user_edit(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(Permission.EDIT_USERS)
    ),
):
    """User edit page."""

    from app.modules.users.services import UserService

    service = UserService(db)

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid user ID")

    user = db.query(UserProfile).filter(
        UserProfile.id == user_uuid,
        UserProfile.company_id == current_user.company_id,
        UserProfile.deleted_at.is_(None),
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    fields = get_model_fields_sqlalchemy(UserProfile)

    context = {
        "request": request,
        "user": user,
        "current_user": current_user,
        "fields": fields,
    }

    return templates.TemplateResponse(
        request=request,
        name="users/edit.html",
        context=sanitize_context(context),
    )


@router.get(
    "/invite",
    response_class=HTMLResponse,
    name="users:invite",
)
async def invite_user(
    request: Request,
    current_user=Depends(
        require_permission(Permission.INVITE_USERS)
    ),
):
    """Invite user page."""

    fields = get_model_fields_sqlalchemy(UserProfile)

    context = {
        "request": request,
        "current_user": current_user,
        "fields": fields,
    }

    return templates.TemplateResponse(
        request=request,
        name="users/invite.html",
        context=sanitize_context(context),
    )


@router.get(
    "/profile",
    response_class=HTMLResponse,
    name="users:profile",
)
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

    return templates.TemplateResponse(
        request=request,
        name="users/profile.html",
        context=sanitize_context(context),
    )
