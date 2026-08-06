"""Notifications module routes."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import get_current_user_profile

router = APIRouter(prefix="/notifications", tags=["Notifications"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="notifications:list")
async def notification_list(
    request: Request,
    current_user=Depends(get_current_user_profile),
):
    return templates.TemplateResponse(request, "notifications/list.html", {
        "current_user": current_user, "notifications": []
    })
