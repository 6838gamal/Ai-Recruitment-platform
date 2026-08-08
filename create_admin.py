"""
Seed script — runs automatically on every startup (via run.py).
Creates a default Company and a super-admin User (with UserProfile)
if they do not already exist.  Safe to run multiple times.
"""

from app.database import SessionLocal
from app.modules.accounts.repositories import UserRepository
from app.modules.companies.models import Company
from app.modules.users.models import UserProfile
from app.core.permissions import UserRole

# ── Default credentials (change after first login) ───────────────────────────
ADMIN_EMAIL = "admin@admin.com"
ADMIN_PASSWORD = "Admin@1234"

# ── Default company ───────────────────────────────────────────────────────────
DEFAULT_COMPANY_NAME = "Default Company"
DEFAULT_COMPANY_SLUG = "default-company"


def _get_or_create_company(db) -> Company:
    """Return the default company, creating it if needed."""
    company = db.query(Company).filter_by(slug=DEFAULT_COMPANY_SLUG).first()
    if company:
        print(f"✓ Default company already exists: {company.name}")
        return company

    company = Company(
        name=DEFAULT_COMPANY_NAME,
        slug=DEFAULT_COMPANY_SLUG,
        timezone="UTC",
        is_active=True,
    )
    db.add(company)
    db.flush()  # get company.id without committing
    print(f"✓ Default company created: {company.name}")
    return company


def main():
    db = SessionLocal()

    try:
        repo = UserRepository(db)

        # ── 1. Ensure default company exists ─────────────────────────────────
        company = _get_or_create_company(db)

        # ── 2. Ensure admin user exists ───────────────────────────────────────
        user = repo.get_by_email(ADMIN_EMAIL)

        if user:
            print(f"✓ Admin user already exists: {user.email}")
        else:
            user = repo.create_user(email=ADMIN_EMAIL, password=ADMIN_PASSWORD)
            user.is_active = True
            user.is_verified = True
            db.flush()
            print(f"✓ Admin user created: {user.email}")

        # ── 3. Ensure admin has a UserProfile linked to the company ───────────
        profile = db.query(UserProfile).filter_by(user_id=user.id).first()

        if profile:
            print(f"✓ Admin profile already exists: {profile.full_name}")
        else:
            profile = UserProfile(
                user_id=user.id,
                company_id=company.id,
                role=UserRole.SUPER_ADMIN.value,
                first_name="Super",
                last_name="Admin",
            )
            db.add(profile)
            print("✓ Admin profile created (Super Admin)")

        db.commit()

        print("")
        print("─" * 40)
        print("  Default login credentials")
        print(f"  Email   : {ADMIN_EMAIL}")
        print(f"  Password: {ADMIN_PASSWORD}")
        print("─" * 40)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
