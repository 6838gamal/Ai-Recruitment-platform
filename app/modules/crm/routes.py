"""CRM module routes."""
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.core.permissions import Permission
from app.database import get_db
from app.dependencies import require_permission
from app.utils.inspect_model import get_model_fields_sqlalchemy
from app.utils.safe_jinja import templates
from app.utils.template_utils import sanitize_context
from app.modules.crm.services import CRMService
from app.modules.crm.models import Client, ClientContact

router = APIRouter(prefix="/crm", tags=["CRM"])


@router.get("/", response_class=HTMLResponse, name="crm:list")
async def client_list(
    request: Request,
    page: int = 1,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.VIEW_COMPANIES)),
):
    """List clients page."""
    service = CRMService(db)
    company_id = current_user.company_id

    clients, total = service.list_clients(
        company_id=company_id,
        page=page,
        per_page=25,
    )

    fields = get_model_fields_sqlalchemy(Client)

    context = {
        "request": request,
        "clients": clients,
        "total": total,
        "page": page,
        "status": status,
        "current_user": current_user,
        "fields": fields,
        "crm_contacts": [],
    }

    return templates.TemplateResponse(
        request=request,
        name="crm/list.html",
        context=sanitize_context(context),
    )


# --- Create routes BEFORE dynamic routes to avoid matching "create" as a dynamic client_id ---
@router.get(
    "/create",
    response_class=HTMLResponse,
    name="crm:create",
)
async def client_create_get(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_JOBS)),
):
    """Render create client form."""
    fields = get_model_fields_sqlalchemy(Client)

    # Create a mock client object with default values for the form
    class MockClient:
        name = ""
        industry = ""
        website = ""
        status = "active"
        notes = ""

    context = {
        "request": request,
        "fields": fields,
        "action": "create",
        "current_user": current_user,
        "error": None,
        "client": MockClient(),
    }

    return templates.TemplateResponse(
        request=request,
        name="crm/form.html",
        context=sanitize_context(context),
    )


@router.post(
    "/create",
    name="crm:create_post",
)
async def client_create_post(
    request: Request,
    name: str = Form(...),
    industry: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    status: str = Form("active"),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_JOBS)),
):
    """Handle create client POST from form."""
    service = CRMService(db)
    data = {
        "name": name.strip(),
        "industry": industry,
        "website": website,
        "status": status,
        "notes": notes,
    }

    try:
        client = service.create_client(current_user.company_id, data)
        db.commit()
    except Exception as e:
        db.rollback()
        fields = get_model_fields_sqlalchemy(Client)
        context = {
            "request": request,
            "fields": fields,
            "action": "create",
            "current_user": current_user,
            "error": str(e),
        }
        return templates.TemplateResponse(
            request=request,
            name="crm/form.html",
            context=sanitize_context(context),
        )

    return RedirectResponse(url=f"/crm/{client.id}", status_code=303)


# --- Dynamic routes (must come AFTER static routes like /create) ---
@router.get(
    "/{client_id}",
    response_class=HTMLResponse,
    name="crm:view",
)
async def client_view(
    request: Request,
    client_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.VIEW_COMPANIES)),
):
    """Client detail view page."""
    service = CRMService(db)

    try:
        client_uuid = uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid client ID")

    client = service.get_client_by_id(client_uuid, current_user.company_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    fields = get_model_fields_sqlalchemy(Client)

    context = {
        "request": request,
        "client": client,
        "current_user": current_user,
        "fields": fields,
    }

    return templates.TemplateResponse(
        request=request,
        name="crm/view.html",
        context=sanitize_context(context),
    )


@router.get(
    "/{client_id}/edit",
    response_class=HTMLResponse,
    name="crm:edit",
)
async def client_edit(
    request: Request,
    client_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_JOBS)),
):
    """Client edit page."""
    service = CRMService(db)

    try:
        client_uuid = uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid client ID")

    client = service.get_client_by_id(client_uuid, current_user.company_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    fields = get_model_fields_sqlalchemy(Client)

    context = {
        "request": request,
        "client": client,
        "current_user": current_user,
        "fields": fields,
        "action": "edit",
    }

    return templates.TemplateResponse(
        request=request,
        name="crm/form.html",
        context=sanitize_context(context),
    )


@router.post(
    "/{client_id}/edit",
    name="crm:update_post",
)
async def client_update_post(
    request: Request,
    client_id: str,
    name: str = Form(...),
    industry: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    status: str = Form("active"),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_JOBS)),
):
    """Handle update client POST from form."""
    service = CRMService(db)

    try:
        client_uuid = uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid client ID")

    data = {
        "name": name.strip(),
        "industry": industry,
        "website": website,
        "status": status,
        "notes": notes,
    }

    try:
        client = service.update_client(client_uuid, current_user.company_id, data)
        db.commit()
    except Exception as e:
        db.rollback()
        client = service.get_client_by_id(client_uuid, current_user.company_id)
        fields = get_model_fields_sqlalchemy(Client)
        context = {
            "request": request,
            "client": client,
            "fields": fields,
            "action": "edit",
            "current_user": current_user,
            "error": str(e),
        }
        return templates.TemplateResponse(
            request=request,
            name="crm/form.html",
            context=sanitize_context(context),
        )

    return RedirectResponse(url=f"/crm/{client.id}", status_code=303)


@router.post(
    "/{client_id}/delete",
    name="crm:delete",
)
async def client_delete(
    request: Request,
    client_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_JOBS)),
):
    """Delete a client."""
    service = CRMService(db)

    try:
        client_uuid = uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid client ID")

    try:
        service.delete_client(client_uuid, current_user.company_id)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    return RedirectResponse(url="/crm", status_code=303)
