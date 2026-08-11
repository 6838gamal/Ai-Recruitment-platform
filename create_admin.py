"""
Seed script — runs automatically on startup via run.py.

Creates:
1. A default Company if it does not already exist.
2. A default super-admin User if it does not already exist.

Safe to run multiple times.
"""

import sys
import traceback

from app.database import SessionLocal
from app.modules.accounts.repositories import UserRepository
from app.modules.companies.models import Company


# ============================================================================
# Default admin credentials
# ============================================================================

ADMIN_EMAIL = "admin@admin.com"
ADMIN_PASSWORD = "Admin@1234"

# ============================================================================
# Default company
# ============================================================================

DEFAULT_COMPANY_NAME = "Default Company"
DEFAULT_COMPANY_SLUG = "default-company"


# ============================================================================
# Helpers
# ============================================================================

def _safe_rollback(db) -> None:
    """Rollback the current transaction without raising another exception."""
    try:
        db.rollback()
    except Exception:
        pass


def _get_or_create_company(db) -> Company | None:
    """
    Get the default company or create it if it does not exist.

    Returns None if the company table cannot be queried.
    """

    try:
        print("\n📋 Checking default company...")

        company = (
            db.query(Company)
            .filter(Company.slug == DEFAULT_COMPANY_SLUG)
            .first()
        )

        if company:
            print(
                f"✓ Default company already exists: "
                f"{company.name} ({company.id})"
            )
            return company

        print(f"  Creating company: {DEFAULT_COMPANY_NAME}")

        company = Company(
            name=DEFAULT_COMPANY_NAME,
            slug=DEFAULT_COMPANY_SLUG,
            timezone="UTC",
            is_active=True,
        )

        db.add(company)
        db.flush()

        print(
            f"✓ Default company created: "
            f"{company.name} ({company.id})"
        )

        return company

    except Exception as exc:
        print(
            "⚠️ Could not create/query default company:"
            f" {str(exc)[:300]}"
        )

        traceback.print_exc()

        _safe_rollback(db)

        return None


def _get_or_create_admin(db):
    """
    Get the default admin user or create it.

    The actual User model is handled through UserRepository,
    so this script does not depend on UserProfile.
    """

    repo = UserRepository(db)

    print("\n📋 Checking default admin user...")

    try:
        user = repo.get_by_email(ADMIN_EMAIL)

    except Exception as exc:
        print(
            f"❌ Failed to query admin user: "
            f"{str(exc)[:300]}"
        )

        traceback.print_exc()
        _safe_rollback(db)

        raise

    if user:
        print(f"✓ Admin user already exists: {user.email}")

        # ------------------------------------------------------------------
        # Keep the existing account active/verified when these fields exist.
        # ------------------------------------------------------------------

        changed = False

        if hasattr(user, "is_active") and not user.is_active:
            user.is_active = True
            changed = True

        if hasattr(user, "is_verified") and not user.is_verified:
            user.is_verified = True
            changed = True

        if changed:
            db.flush()
            print("✓ Admin account status updated.")

        return user

    # ------------------------------------------------------------------------
    # Create admin user
    # ------------------------------------------------------------------------

    print(f"  Creating admin user: {ADMIN_EMAIL}")

    try:
        user = repo.create_user(
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD,
        )

        # Activate / verify when the fields exist.
        if hasattr(user, "is_active"):
            user.is_active = True

        if hasattr(user, "is_verified"):
            user.is_verified = True

        db.flush()

        print(
            f"✓ Admin user created successfully "
            f"(id={user.id})"
        )

        return user

    except Exception as exc:
        print(
            f"❌ Failed to create admin user: "
            f"{str(exc)[:300]}"
        )

        traceback.print_exc()

        _safe_rollback(db)

        raise


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    """Initialize default company and admin user."""

    db = SessionLocal()

    try:
        print("")
        print("=" * 60)
        print("🔄 Starting admin initialization")
        print("=" * 60)

        # --------------------------------------------------------------------
        # 1. Default company
        # --------------------------------------------------------------------

        company = _get_or_create_company(db)

        if company:
            print(
                f"✓ Company ready: "
                f"{company.name}"
            )
        else:
            print(
                "⚠️ Company initialization was skipped."
            )

        # --------------------------------------------------------------------
        # 2. Default admin user
        # --------------------------------------------------------------------

        admin = _get_or_create_admin(db)

        # --------------------------------------------------------------------
        # 3. Commit
        # --------------------------------------------------------------------

        print("\n📋 Committing changes...")

        db.commit()

        print("✓ Database transaction committed.")

        # --------------------------------------------------------------------
        # 4. Information
        # --------------------------------------------------------------------

        print("")
        print("=" * 60)
        print("  Default Admin Credentials")
        print("=" * 60)
        print(f"  Email    : {ADMIN_EMAIL}")
        print(f"  Password : {ADMIN_PASSWORD}")
        print("=" * 60)
        print("")

        print("✅ Admin initialization completed successfully.")

    except Exception as exc:
        print("")
        print("=" * 60)
        print("❌ Admin initialization failed")
        print("=" * 60)
        print(f"Error: {str(exc)[:500]}")
        print("=" * 60)

        traceback.print_exc()

        _safe_rollback(db)

        # Important:
        # Returning a non-zero exit code makes Render detect
        # the initialization failure.
        sys.exit(1)

    finally:
        db.close()
        print("Database session closed.")


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    main()
