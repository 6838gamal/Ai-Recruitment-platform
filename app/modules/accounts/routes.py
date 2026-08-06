"""Accounts module routes — login, logout, password management."""
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import (
    AccountLockedError,
    AuthenticationError,
    InvalidTokenError,
    ValidationError,
)
from app.database import get_db
from app.dependencies import get_current_user_profile
from app.modules.accounts.schemas import (
    ChangePasswordSchema,
    ForgotPasswordSchema,
    LoginSchema,
    ResetPasswordSchema,
)
from app.modules.accounts.services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
templates = Jinja2Templates(directory="app/templates")


# ─── Helper ───────────────────────────────────────────────────────────────────

def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Set JWT cookies on response."""
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )


def clear_auth_cookies(response: Response) -> None:
    """Clear JWT cookies."""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


# ─── Login ────────────────────────────────────────────────────────────────────

@router.get("/login", response_class=HTMLResponse, name="auth:login_page")
async def login_page(request: Request):
    """Render the login page."""
    # Redirect if already logged in
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(request, "auth/login.html", {"error": None})


@router.post("/login", name="auth:login")
async def login(
    request: Request,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    remember_me: Annotated[bool, Form()] = False,
    db: Session = Depends(get_db),
):
    """Process login form submission."""
    login_data = LoginSchema(email=email, password=password, remember_me=remember_me)
    service = AuthService(db)

    try:
        access_token, refresh_token, user = service.login(login_data, request=request)
    except (AuthenticationError, AccountLockedError) as e:
        return templates.TemplateResponse(
            request, "auth/login.html",
            {"error": str(e)},
            status_code=400,
        )

    response = RedirectResponse(url="/dashboard", status_code=303)
    set_auth_cookies(response, access_token, refresh_token)
    return response


# ─── Logout ───────────────────────────────────────────────────────────────────

@router.post("/logout", name="auth:logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    """Log out the current user."""
    refresh_token = request.cookies.get("refresh_token", "")
    if refresh_token:
        service = AuthService(db)
        service.logout(refresh_token)

    response = RedirectResponse(url="/auth/login", status_code=303)
    clear_auth_cookies(response)
    return response


# ─── Forgot Password ──────────────────────────────────────────────────────────

@router.get("/forgot-password", response_class=HTMLResponse, name="auth:forgot_password_page")
async def forgot_password_page(request: Request):
    """Render the forgot password page."""
    return templates.TemplateResponse(
        request, "auth/forgot_password.html",
        {"submitted": False, "error": None},
    )


@router.post("/forgot-password", name="auth:forgot_password")
async def forgot_password(
    request: Request,
    background_tasks: BackgroundTasks,
    email: Annotated[str, Form()],
    db: Session = Depends(get_db),
):
    """Process forgot password form."""
    service = AuthService(db)
    try:
        data = ForgotPasswordSchema(email=email)
        service.initiate_password_reset(data, background_tasks=background_tasks)
    except Exception:
        pass  # Silent fail for security

    return templates.TemplateResponse(
        request, "auth/forgot_password.html",
        {"submitted": True, "error": None},
    )


# ─── Reset Password ───────────────────────────────────────────────────────────

@router.get("/reset-password", response_class=HTMLResponse, name="auth:reset_password_page")
async def reset_password_page(request: Request, token: str = ""):
    """Render the reset password page."""
    if not token:
        return RedirectResponse(url="/auth/forgot-password", status_code=302)
    return templates.TemplateResponse(
        request, "auth/reset_password.html",
        {"token": token, "error": None, "success": False},
    )


@router.post("/reset-password", name="auth:reset_password")
async def reset_password(
    request: Request,
    token: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
    confirm_password: Annotated[str, Form()],
    db: Session = Depends(get_db),
):
    """Process the password reset form."""
    service = AuthService(db)
    try:
        data = ResetPasswordSchema(
            token=token,
            new_password=new_password,
            confirm_password=confirm_password,
        )
        service.reset_password(data)
    except (InvalidTokenError, ValidationError) as e:
        return templates.TemplateResponse(
            request, "auth/reset_password.html",
            {"token": token, "error": str(e), "success": False},
            status_code=400,
        )
    except Exception as e:
        return templates.TemplateResponse(
            request, "auth/reset_password.html",
            {"token": token, "error": "An error occurred. Please try again.", "success": False},
            status_code=400,
        )

    return templates.TemplateResponse(
        request, "auth/reset_password.html",
        {"token": token, "error": None, "success": True},
    )


# ─── API Endpoints ────────────────────────────────────────────────────────────

@router.post("/refresh", tags=["Authentication API"])
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    """Refresh access token using refresh token cookie."""
    raw_refresh = request.cookies.get("refresh_token")
    if not raw_refresh:
        raise HTTPException(status_code=401, detail="No refresh token")

    service = AuthService(db)
    try:
        new_access, new_refresh = service.refresh_access_token(raw_refresh)
    except (InvalidTokenError, AuthenticationError) as e:
        response = Response(status_code=401)
        clear_auth_cookies(response)
        raise HTTPException(status_code=401, detail=str(e))

    response = Response(content='{"success": true}', media_type="application/json")
    set_auth_cookies(response, new_access, new_refresh)
    return response
