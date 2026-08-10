"""Dashboard module routes."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_profile
from app.utils.safe_jinja import templates


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# Ensure attribute is available in templates
if "attribute" not in templates.env.globals:
    templates.env.globals["attribute"] = getattr


# Support both /dashboard and /dashboard/
@router.get(
    "",
    response_class=HTMLResponse,
    include_in_schema=False,
)
@router.get(
    "/",
    response_class=HTMLResponse,
    name="dashboard:index",
)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Main dashboard page with dynamic data."""

    from app.modules.dashboard.services import DashboardService

    service = DashboardService(db)

    stats = service.get_stats(
        current_user.company_id
    )

    recent_activities = service.get_recent_activities(
        current_user.company_id
    )

    # Permissions for quick actions.
    # Replace these with real permission checks when available.
    permissions = {
        "can_create_jobs": True,
        "can_create_candidates": True,
        "can_schedule_interviews": True,
        "can_use_ai_matching": True,
    }

    context = {
        "request": request,
        "current_user": current_user,
        "stats": stats,
        "recent_activities": recent_activities,
        "permissions": permissions,
    }

    return templates.TemplateResponse(
        request=request,
        name="dashboard/index.html",
        context=context,
    )
