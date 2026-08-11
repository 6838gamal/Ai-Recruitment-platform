"""Application entry point for development and production."""

import os
import subprocess
import sys

import uvicorn

from app.config import settings
from app.database import Base, engine


def run_migrations() -> None:
    """Apply database migrations before starting the application."""
    print("🔄 Applying database migrations...")

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=False,
    )

    if result.returncode != 0:
        print("❌ Database migrations failed.")
        sys.exit(result.returncode)

    print("✅ Database migrations completed.")


def create_missing_tables() -> None:
    """Create database tables that do not exist yet."""
    print("🗄️ Checking database tables...")

    # Import all models so SQLAlchemy registers them
    # in Base.metadata before create_all() is called.
    from app.modules.accounts import models as accounts_models  # noqa: F401
    from app.modules.companies import models as companies_models  # noqa: F401
    from app.modules.users import models as users_models  # noqa: F401
    from app.modules.jobs import models as jobs_models  # noqa: F401
    from app.modules.candidates import models as candidates_models  # noqa: F401
    from app.modules.ats import models as ats_models  # noqa: F401
    from app.modules.interviews import models as interviews_models  # noqa: F401
    from app.modules.notifications import models as notifications_models  # noqa: F401
    from app.modules.ai_matching import models as ai_models  # noqa: F401
    from app.modules.files import models as files_models  # noqa: F401
    from app.modules.audit import models as audit_models  # noqa: F401
    from app.modules.crm import models as crm_models  # noqa: F401
    from app.modules.billing import models as billing_models  # noqa: F401
    from app.modules.settings import models as settings_models  # noqa: F401
    from app.modules.resume_parser import models as resume_parser_models  # noqa: F401

    # Create only missing tables.
    # Existing tables are NOT deleted or modified.
    Base.metadata.create_all(bind=engine)

    print("✅ Database tables checked.")


def create_admin() -> None:
    """Create the default admin user if it does not exist."""
    print("👤 Checking default admin user...")

    result = subprocess.run(
        [sys.executable, "create_admin.py"],
        check=False,
    )

    if result.returncode != 0:
        print("❌ Admin user initialization failed.")
        sys.exit(result.returncode)

    print("✅ Admin user is ready.")


def main() -> None:
    """Initialize the application and start Uvicorn."""

    # 1. Apply Alembic migrations
    run_migrations()

    # 2. Create any missing database tables
    create_missing_tables()

    # 3. Ensure default admin exists
    create_admin()

    # 4. Start FastAPI
    print("\n🚀 Starting AI Recruitment Platform...")
    print(f"   Environment: {settings.APP_ENV}")
    print(f"   Debug: {settings.DEBUG}")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        reload=settings.is_development,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    main()
