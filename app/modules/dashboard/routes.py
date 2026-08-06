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
    """Main dashboard page."""
    from app.modules.dashboard.services import DashboardService
    service = DashboardService(db)
    stats = service.get_stats(current_user.company_id)

    return templates.TemplateResponse(request, "dashboard/index.html", {
        "current_user": current_user,
        "stats": stats,
    })
