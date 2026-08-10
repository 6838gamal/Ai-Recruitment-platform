"""
Seed script — runs automatically on every startup (via run.py).
Creates a default Company and a super-admin User (with UserProfile)
if they do not already exist. Safe to run multiple times.
"""

import sys
import traceback

from app.database import SessionLocal
from app.modules.accounts.repositories import UserRepository
from app.modules.companies.models import Company
from app.modules.users.models import UserProfile
from app.core.permissions import UserRole

# ── Default credentials (change after first login) ───────────────────────────
ADMIN_EMAIL = "admin@admin.com"
ADMIN_PASSWORD = "Admin@1234"

# ── Default company ─────────────────────────────────────────────────────────
DEFAULT_COMPANY_NAME = "Default Company"
DEFAULT_COMPANY_SLUG = "default-company"


def _get_or_create_company(db) -> Company:
    """Return the default company, creating it if needed."""
    try:
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
    except Exception as e:
        print(f"❌ Error creating company: {str(e)}")
        traceback.print_exc()
        raise


def main():
    db = SessionLocal()

    try:
        repo = UserRepository(db)

        # ── 1. Ensure default company exists ─────────────────────────────────
        company = _get_or_create_company(db)

        # ── 2. Ensure admin user exists ───────────────────────────────────────
        try:
            user = repo.get_by_email(ADMIN_EMAIL)
        except Exception as e:
            print(f"❌ Error querying user: {str(e)}")
            traceback.print_exc()
            raise

        if user:
            print(f"✓ Admin user already exists: {user.email}")
        else:
            try:
                user = repo.create_user(email=ADMIN_EMAIL, password=ADMIN_PASSWORD)
                user.is_active = True
                user.is_verified = True
                db.flush()
                print(f"✓ Admin user created: {user.email}")
            except Exception as e:
                print(f"❌ Error creating user: {str(e)}")
                traceback.print_exc()
                raise

        # ── 3. Ensure admin has a UserProfile linked to the company ───────────
        try:
            profile = db.query(UserProfile).filter_by(user_id=user.id).first()
        except Exception as e:
            print(f"❌ Error querying UserProfile: {str(e)}")
            traceback.print_exc()
            raise

        if profile:
            print(f"✓ Admin profile already exists: {profile.full_name}")
        else:
            try:
                profile = UserProfile(
                    user_id=user.id,
                    company_id=company.id,
                    role=UserRole.SUPER_ADMIN.value,
                    first_name="Super",
                    last_name="Admin",
                )
                db.add(profile)
                print("✓ Admin profile created (Super Admin)")
            except Exception as e:
                print(f"❌ Error creating UserProfile: {str(e)}")
                traceback.print_exc()
                raise

        db.commit()

        print("")
        print("─" * 40)
        print("  Default login credentials")
        print(f"  Email   : {ADMIN_EMAIL}")
        print(f"  Password: {ADMIN_PASSWORD}")
        print("─" * 40)
        print("✅ Admin user initialization completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Admin user initialization failed: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()
