"""Application entry point for development and production."""

import os
import subprocess
import sys

import uvicorn

from app.config import settings


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

    # Prepare database
    run_migrations()

    # Ensure default admin exists
    create_admin()

    # Start FastAPI
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
