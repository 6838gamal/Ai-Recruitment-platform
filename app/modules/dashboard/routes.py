"""Dashboard module routes."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_profile
from app.utils.safe_jinja import templates
from app.utils.template_utils import sanitize_context

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# ensure attribute available in templates
if "attribute" not in templates.env.globals:
    templates.env.globals["attribute"] = getattr

# Register both "" and "/" so clients won't get 405 due to trailing-slash mismatches
@router.get("", include_in_schema=False)
@router.get("/", response_class=HTMLResponse, name="dashboard:index")
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_profile),
):
    """Main dashboard page with dynamic data."""
    from app.modules.dashboard.services import DashboardService

    service = DashboardService(db)
    stats = service.get_stats(current_user.company_id)
    recent_activities = service.get_recent_activities(current_user.company_id)

    # Permissions for quick actions (replace with real permission checks as needed)
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

    return templates.TemplateResponse("dashboard/index.html", sanitize_context(context))
