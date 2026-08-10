"""Dashboard module routes."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_profile

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")


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
    
    # Permissions for quick actions
    permissions = {
        "can_create_jobs": True,  # Should be based on actual permissions
        "can_create_candidates": True,
        "can_schedule_interviews": True,
        "can_use_ai_matching": True,
    }

    return templates.TemplateResponse(
        "dashboard/index.html",
        {
            "request": request,
            "current_user": current_user,
            "stats": stats,
            "recent_activities": recent_activities,
            "permissions": permissions,
        },
    )
