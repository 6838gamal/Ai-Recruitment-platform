from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.utils.enhanced_templates import EnhancedJinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.accounts.services import AuthService
from app.modules.accounts.schemas import LoginSchema
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])
templates = EnhancedJinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    """Render the login page."""
    return templates.TemplateResponse(request, "auth/login.html", {"request": request})


@router.post("/login")
async def post_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    remember_me: str = Form(None),
    db: Session = Depends(get_db),
):
    """Handle login form submission and set auth cookies on success."""
    service = AuthService(db)

    data = LoginSchema(email=email, password=password)
    try:
        access_token, refresh_token, user = service.login(data, request=request)
    except Exception as exc:
        # On failure, re-render login with error message
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"request": request, "error": str(exc)},
        )

    # Successful login — set cookies and redirect to dashboard
    response = RedirectResponse(url="/dashboard", status_code=302)

    # Cookie settings
    secure = not settings.DEBUG
    max_age = 60 * 60 * 24 * 7 if remember_me else 60 * 15  # 7 days vs short-lived

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
        max_age=max_age,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24 * settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    )

    return response


@router.post("/logout")
async def post_logout(request: Request, db: Session = Depends(get_db)):
    """Logout: revoke refresh token (if present) and clear cookies."""
    service = AuthService(db)
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            service.logout(refresh_token)
        except Exception:
            pass

    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    response.delete_cookie("session", path="/")
    return response
