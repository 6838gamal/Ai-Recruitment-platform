from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from urllib.parse import quote_plus
from jinja2 import TemplateNotFound

from app.database import get_db
from app.utils.enhanced_templates import EnhancedJinja2Templates
from app.modules.users.repositories import UserProfileRepository
from app.modules.users.models import UserProfile
from app.utils.inspect_model import get_model_fields_sqlalchemy
from app.dependencies import get_current_user_profile

router = APIRouter(prefix="/users", tags=["Users"])
templates = EnhancedJinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="users:list")
async def list_users(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user_profile)):
    repo = UserProfileRepository(db)
    users = []
    try:
        if current_user:
            users = repo.get_by_company(current_user.company_id)
        else:
            users = repo.get_all()  # fallback to all if available
    except Exception:
        # best-effort: return empty list on repository issues
        users = []

    fields = get_model_fields_sqlalchemy(UserProfile)

    try:
        return templates.TemplateResponse(
            request,
            "users/list.html",
            {"request": request, "users": users, "fields": fields, "current_user": current_user, "attribute": getattr},
        )
    except TemplateNotFound:
        # Template missing: return a JSON fallback so FastAPI/Starlette can serialize it
        return JSONResponse({"message": "Users list endpoint", "count": len(users)})
    except Exception:
        # Unexpected error while rendering template — re-raise so it's handled by error middleware
        raise


@router.get("/create", response_class=HTMLResponse, name="users:create_form")
async def create_user_form(request: Request, current_user=Depends(get_current_user_profile)):
    fields = get_model_fields_sqlalchemy(UserProfile)
    return templates.TemplateResponse(
        request,
        "users/form.html",
        {"request": request, "action": "create", "fields": fields, "current_user": current_user, "attribute": getattr},
    )


@router.post("/create")
async def create_user_submit(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user_profile)):
    form = await request.form()

    data = {
        "user_id": form.get("user_id"),
        "company_id": current_user.company_id if current_user else None,
        "role": form.get("role") or "user",
        "first_name": form.get("first_name"),
        "last_name": form.get("last_name"),
        "phone": form.get("phone"),
        "avatar_url": None,
        "job_title": form.get("job_title"),
        "department": form.get("department"),
    }

    repo = UserProfileRepository(db)
    try:
        profile = repo.create(data)
        return RedirectResponse(url=f"/users/{quote_plus(str(profile.id))}", status_code=302)
    except IntegrityError as exc:
        db.rollback()
        fields = get_model_fields_sqlalchemy(UserProfile)
        error = str(exc)
        return templates.TemplateResponse(
            request,
            "users/form.html",
            {"request": request, "action": "create", "fields": fields, "error": error, "form_values": form, "current_user": current_user, "attribute": getattr},
        )


@router.get("/{id}", response_class=HTMLResponse, name="users:detail")
async def user_detail(request: Request, id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user_profile)):
    repo = UserProfileRepository(db)
    profile = repo.get(id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    fields = get_model_fields_sqlalchemy(UserProfile)
    return templates.TemplateResponse(
        request,
        "users/detail.html",
        {"request": request, "user": profile, "fields": fields, "current_user": current_user, "attribute": getattr},
    )


@router.get("/{id}/edit", response_class=HTMLResponse, name="users:edit_form")
async def edit_user_form(request: Request, id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user_profile)):
    repo = UserProfileRepository(db)
    profile = repo.get(id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    fields = get_model_fields_sqlalchemy(UserProfile)
    return templates.TemplateResponse(
        request,
        "users/form.html",
        {"request": request, "action": "edit", "user": profile, "fields": fields, "current_user": current_user, "attribute": getattr},
    )


@router.post("/{id}/edit")
async def edit_user_submit(request: Request, id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user_profile)):
    form = await request.form()
    repo = UserProfileRepository(db)
    profile = repo.get(id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")

    data = {
        "first_name": form.get("first_name") or profile.first_name,
        "last_name": form.get("last_name") or profile.last_name,
        "phone": form.get("phone") or profile.phone,
        "job_title": form.get("job_title") or profile.job_title,
        "department": form.get("department") or profile.department,
        "role": form.get("role") or profile.role,
    }
    try:
        updated = repo.update(profile, data)
        return RedirectResponse(url=f"/users/{quote_plus(str(updated.id))}", status_code=302)
    except IntegrityError as exc:
        db.rollback()
        fields = get_model_fields_sqlalchemy(UserProfile)
        error = str(exc)
        return templates.TemplateResponse(
            request,
            "users/form.html",
            {"request": request, "action": "edit", "user": profile, "fields": fields, "error": error, "form_values": form, "current_user": current_user, "attribute": getattr},
        )


@router.post("/{id}/delete")
async def delete_user(request: Request, id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user_profile)):
    repo = UserProfileRepository(db)
    profile = repo.get(id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    repo.soft_delete(profile)
    return RedirectResponse(url="/users/", status_code=302)
