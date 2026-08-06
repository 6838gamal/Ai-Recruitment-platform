"""
AI Recruitment Platform — FastAPI Application Entry Point.

Modular Monolith architecture: one application, 17 internal modules.
"""
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.core.exceptions import AppException
from app.middleware import RequestTimingMiddleware, SecurityHeadersMiddleware

# ─── Rate Limiter ─────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


# ─── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan events."""
    # Create upload directories
    os.makedirs(settings.LOCAL_UPLOAD_DIR, exist_ok=True)

    # Ensure database tables exist (for development convenience)
    # Migrations are managed by Alembic
    from app.database import engine, Base
    # Only auto-create in development if tables don't exist
    # In production, always use: alembic upgrade head

    print(f"🚀 {settings.APP_NAME} starting up...")
    print(f"   Environment: {settings.APP_ENV}")
    print(f"   Debug: {settings.DEBUG}")

    yield

    print("👋 Application shutting down...")


# ─── FastAPI Application ───────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered recruitment and HR management platform",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ─── Middleware ────────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

# ─── Static Files ─────────────────────────────────────────────────────────────
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ─── Templates ────────────────────────────────────────────────────────────────
templates = Jinja2Templates(directory="app/templates")

# ─── Exception Handlers ───────────────────────────────────────────────────────

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle domain exceptions."""
    from fastapi.responses import JSONResponse
    if request.headers.get("HX-Request"):
        return HTMLResponse(
            content=f'<div class="alert alert-error">{exc.message}</div>',
            status_code=exc.status_code,
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith("/api/"):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=404, content={"success": False, "error": {"message": "Not found"}})
    return templates.TemplateResponse("errors/404.html", {"request": request}, status_code=404)


@app.exception_handler(500)
async def server_error_handler(request: Request, exc: Exception):
    if settings.DEBUG:
        raise exc
    return templates.TemplateResponse("errors/500.html", {"request": request}, status_code=500)


# ─── Root Redirect ────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root(request: Request):
    """Redirect root to dashboard (or login if not authenticated)."""
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse(url="/dashboard", status_code=302)
    return RedirectResponse(url="/auth/login", status_code=302)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}


# ─── Module Routers ───────────────────────────────────────────────────────────

from app.modules.accounts.routes import router as auth_router
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
