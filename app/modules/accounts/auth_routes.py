"""Authentication routes."""

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.utils.enhanced_templates import EnhancedJinja2Templates
from app.database import get_db
from app.modules.accounts.services import AuthService
from app.modules.accounts.schemas import LoginSchema
from app.config import settings


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

templates = EnhancedJinja2Templates(
    directory="app/templates"
)


@router.get(
    "/login",
    response_class=HTMLResponse,
)
async def get_login(request: Request):
    """Render the login page."""

    return templates.TemplateResponse(
        request,
        "auth/login.html",
        {
            "request": request,
        },
    )


@router.post("/login")
async def post_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    remember_me: str = Form(None),
    db: Session = Depends(get_db),
):
    """Authenticate user and create authentication cookies."""

    service = AuthService(db)

    data = LoginSchema(
        email=email,
        password=password,
    )

    try:
        access_token, refresh_token, user = service.login(
            data,
            request=request,
        )

    except Exception as exc:
        db.rollback()

        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {
                "request": request,
                "error": str(exc),
                "email": email,
            },
            status_code=401,
        )

    # ---------------------------------------------------------
    # Validate authenticated user
    # ---------------------------------------------------------

    if not user:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {
                "request": request,
                "error": "تعذر تحديد المستخدم بعد تسجيل الدخول.",
                "email": email,
            },
            status_code=401,
        )

    if not getattr(user, "id", None):
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {
                "request": request,
                "error": "حساب المستخدم غير صالح.",
                "email": email,
            },
            status_code=401,
        )

    # ---------------------------------------------------------
    # Successful login
    # ---------------------------------------------------------

    response = RedirectResponse(
        url="/dashboard",
        status_code=302,
    )

    secure = not settings.DEBUG

    access_max_age = (
        60 * 60 * 24 * 7
        if remember_me
        else 60 * 15
    )

    refresh_max_age = (
        60
        * 60
        * 24
        * settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )

    # ---------------------------------------------------------
    # Access token
    # ---------------------------------------------------------

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
        max_age=access_max_age,
    )

    # ---------------------------------------------------------
    # Refresh token
    # ---------------------------------------------------------

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
        max_age=refresh_max_age,
    )

    return response


@router.post("/logout")
async def post_logout(
    request: Request,
    db: Session = Depends(get_db),
):
    """Logout user and clear authentication cookies."""

    service = AuthService(db)

    refresh_token = request.cookies.get(
        "refresh_token"
    )

    if refresh_token:

        try:
            service.logout(refresh_token)
        except Exception:
            db.rollback()

    response = RedirectResponse(
        url="/auth/login",
        status_code=302,
    )

    response.delete_cookie(
        key="access_token",
        path="/",
    )

    response.delete_cookie(
        key="refresh_token",
        path="/",
    )

    response.delete_cookie(
        key="session",
        path="/",
    )

    return response
