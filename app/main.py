"""
AI Recruitment Platform — FastAPI Application Entry Point.

Modular Monolith architecture: one application, 17 internal modules.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.core.exceptions import AppException
from app.middleware import (
    RequestTimingMiddleware,
    SecurityHeadersMiddleware,
)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan events."""

    os.makedirs(settings.LOCAL_UPLOAD_DIR, exist_ok=True)
    os.makedirs("static", exist_ok=True)

    print(f"🚀 {settings.APP_NAME} starting up...")
    print(f"   Environment: {settings.APP_ENV}")
    print(f"   Debug: {settings.DEBUG}")

    yield

    print("👋 Application shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered recruitment and HR management platform",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)


app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestTimingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
)


os.makedirs("static", exist_ok=True)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


templates = Jinja2Templates(
    directory="app/templates"
)

# Robust workaround: wrap the Jinja2 environment's get_template so that any
# globals passed by Starlette/TemplateResponse are sanitized to contain only
# hashable keys/values for the Jinja2 cache key. This keeps TemplateResponse
# behavior intact (deferred rendering, middleware integration) while avoiding
# "unhashable type: 'dict'" errors coming from Jinja2's internal cache.
env = getattr(templates, "env", None) or getattr(templates, "environment", None)
if env is not None:
    _orig_get_template = env.get_template

    class _HashableWrapper:
        """Make an unhashable object appear hashable for use in Jinja2 cache keys

        The wrapper delegates attribute/item access to the original object so
        templates can still read values normally, while providing a stable
        __hash__ implementation (based on id()).
        """

        def __init__(self, obj):
            self._obj = obj

        def __getattr__(self, name):
            return getattr(self._obj, name)

        def __iter__(self):
            return iter(self._obj)

        def __len__(self):
            try:
                return len(self._obj)
            except Exception:
                return 0

        def __getitem__(self, key):
            return self._obj[key]

        def __repr__(self):
            return repr(self._obj)

        def __hash__(self):
            # id() is stable during the lifetime of the process and is fine
            # for differentiating cache keys in this context.
            return id(self._obj)

    def _sanitize_globals(globals_mapping):
        if not globals_mapping:
            return globals_mapping
        safe = {}
        for k, v in globals_mapping.items():
            try:
                hash(v)
                safe[k] = v
            except Exception:
                # Wrap unhashable values so they won't break Jinja2's cache key
                safe[k] = _HashableWrapper(v)
        return safe

    def _safe_get_template(name, globals=None):
        # Avoid passing per-call globals to Jinja2's get_template to prevent
        # unhashable objects from entering the template cache key. Starlette's
        # TemplateResponse will still work because we only control template
        # lookup here; template rendering receives the context later.
        return _orig_get_template(name)

    # Patch the environment's get_template in place.
    env.get_template = _safe_get_template


@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    """Handle application/domain exceptions."""

    if request.headers.get("HX-Request"):
        return HTMLResponse(
            content=exc.message,
            status_code=exc.status_code,
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        },
    )


@app.exception_handler(401)
async def unauthorized_handler(request: Request, exc: HTTPException):
    """
    معالج استثناء موحد للـ 401 (عدم المصادقة / انتهاء الجلسة)
    
    يقوم بـ:
    1. تحويل المستخدم إلى صفحة تسجيل الدخول للصفحات المرئية
    2. إرجاع JSON error للـ API
    3. حذف cookies الجلسة (اختياري)
    """
    
    # إذا كان طلب API (AJAX/JSON)
    if request.headers.get("Accept", "").startswith("application/json") or \
       request.headers.get("HX-Request"):
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "جلستك انتهت. يرجى تسجيل الدخول مجددًا",
                },
            },
        )
    
    # إذا كان صفحة مرئية (HTML)
    # تحويل المستخدم مباشرة إلى صفحة تسجيل الدخول
    response = RedirectResponse(
        url="/auth/login",
        status_code=302,
    )
    
    # حذف cookies الجلسة
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("session", path="/")
    
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """معالج استثناء HTTP عام - يتعامل مع جميع HTTPException بما فيها 401 و 403"""
    
    # معالجة خاصة لـ 401
    if exc.status_code == 401:
        # إذا كان طلب API
        if request.headers.get("Accept", "").startswith("application/json") or \
           request.headers.get("HX-Request"):
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "جلستك انتهت. يرجى تسجيل الدخول مجددًا",
                    },
                },
            )
        
        # تحويل صفحات HTML إلى login
        response = RedirectResponse(url="/auth/login", status_code=302)
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("session", path="/")
        return response
    
    # معالجة خاصة لـ 403 (الوصول مرفوع)
    if exc.status_code == 403:
        if request.headers.get("Accept", "").startswith("application/json") or \
           request.headers.get("HX-Request"):
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "ليس لديك صلاحيات للوصول إلى هذا المورد",
                    },
                },
            )
        
        return templates.TemplateResponse(
            "errors/403.html",
            {"request": request, "error": exc.detail},
            status_code=403,
        )
    
    # معالجة 404
    if exc.status_code == 404:
        if request.headers.get("Accept", "").startswith("application/json"):
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "الصفحة غير موجودة",
                    },
                },
            )
        
        return templates.TemplateResponse(
            "errors/404.html",
            {"request": request},
            status_code=404,
        )
    
    # للأخطاء الأخرى
    if request.headers.get("Accept", "").startswith("application/json"):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": "HTTP_ERROR",
                    "message": exc.detail or "حدث خطأ",
                },
            },
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
        },
    )


@app.get("/", include_in_schema=False)
async def root(request: Request):
    """Redirect root to dashboard or login."""

    token = request.cookies.get("access_token")

    if token:
        return RedirectResponse(
            url="/dashboard",
            status_code=302,
        )

    return RedirectResponse(
        url="/auth/login",
        status_code=302,
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for deployment monitoring."""

    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
    }


from app.modules.accounts import models as _accounts_models
from app.modules.users import models as _users_models
from app.modules.companies import models as _companies_models
from app.modules.jobs import models as _jobs_models
from app.modules.candidates import models as _candidates_models
from app.modules.ats import models as _ats_models
from app.modules.interviews import models as _interviews_models
from app.modules.billing import models as _billing_models
from app.modules.crm import models as _crm_models
from app.modules.notifications import models as _notifications_models
from app.modules.audit import models as _audit_models
from app.modules.files import models as _files_models
from app.modules.ai_matching import models as _ai_models
from app.modules.settings import models as _settings_models


from app.modules.accounts.auth_routes import router as auth_router
from app.modules.users.routes import router as users_router
from app.modules.companies.routes import router as companies_router
from app.modules.jobs.routes import router as jobs_router
from app.modules.candidates.routes import router as candidates_router
from app.modules.resume_parser.routes import router as resume_parser_router
from app.modules.ai_matching.routes import router as ai_matching_router
from app.modules.ats.routes import router as ats_router
from app.modules.interviews.routes import router as interviews_router
from app.modules.notifications.routes import router as notifications_router
from app.modules.crm.routes import router as crm_router
from app.modules.billing.routes import router as billing_router
from app.modules.reports.routes import router as reports_router
from app.modules.dashboard.routes import router as dashboard_router
from app.modules.files.routes import router as files_router
from app.modules.audit.routes import router as audit_router
from app.modules.settings.routes import router as settings_router


app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(users_router)
app.include_router(companies_router)
app.include_router(jobs_router)
app.include_router(candidates_router)
app.include_router(resume_parser_router)
app.include_router(ai_matching_router)
app.include_router(ats_router)
app.include_router(interviews_router)
app.include_router(notifications_router)
app.include_router(crm_router)
app.include_router(billing_router)
app.include_router(reports_router)
app.include_router(files_router)
app.include_router(audit_router)
app.include_router(settings_router)
