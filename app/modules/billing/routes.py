"""Billing module routes."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.permissions import Permission
from app.dependencies import require_permission

router = APIRouter(prefix="/billing", tags=["Billing"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="billing:invoices")
async def invoice_list(
    request: Request,
    current_user=Depends(require_permission(Permission.VIEW_BILLING)),
):
    return templates.TemplateResponse("billing/list.html", {
        "request": request, "current_user": current_user, "invoices": []
    })
