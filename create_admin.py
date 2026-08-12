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


def _safe_rollback(db):
    """Attempt to rollback the DB session, ignoring errors.

    Many SQLAlchemy errors leave the transaction in an aborted state and
    subsequent queries will fail until a rollback is performed. Call this
    helper from any exception handler that wants to continue using the
    session.
    """
    try:
        db.rollback()
    except Exception:
        # Best-effort only; don't raise from the rollback attempt
        pass


def _get_or_create_company(db) -> Company:
    """Return the default company, creating it if needed."""
    try:
        print("\n📋 Attempting to query existing company...")
        # Try to query, but catch if the table structure doesn't match yet
        try:
            company = db.query(Company).filter_by(slug=DEFAULT_COMPANY_SLUG).first()
        except Exception as query_error:
            print(f"  ⚠️  Could not query companies table (migrations may be incomplete)")
            print(f"     This is OK - we'll skip company creation for now.")
            print(f"     Error: {str(query_error)[:100]}...")
            # rollback the session so subsequent queries can proceed
            _safe_rollback(db)
            return None  # Return None if we can't query the table

        if company:
            print(f"✓ Default company already exists: {company.name}")
            return company

        print(f"  Creating new company: {DEFAULT_COMPANY_NAME}")
        company = Company(
            name=DEFAULT_COMPANY_NAME,
            slug=DEFAULT_COMPANY_SLUG,
            timezone="UTC",
            is_active=True,
        )
        db.add(company)
        db.flush()  # get company.id without committing
        print(f"✓ Default company created: {company.name} (id={company.id})")
        return company
    except Exception as e:
        print(f"⚠️  Error creating company: {str(e)[:200]}...")
        print(f"   This might be due to incomplete migrations. Continuing anyway...")
        # ensure any partial transaction is cleared
        _safe_rollback(db)
        return None


def main():
    db = SessionLocal()

    try:
        print("\n🔄 Starting admin initialization...")
        repo = UserRepository(db)

        # ── 1. Try to ensure default company exists ─────────────────────────────────
        print("\n📋 Step 1: Attempting to ensure default company exists...")
        company = _get_or_create_company(db)
        if company is None:
            print("   Note: Company creation skipped due to table structure mismatch.")
            print("   This is expected if migrations are still being applied.")
            company_id = None
        else:
            company_id = company.id

        # ── 2. Ensure admin user exists ───────────────────────────────────────────────
        print("\n📋 Step 2: Checking for admin user...")
        try:
            user = repo.get_by_email(ADMIN_EMAIL)
            print(f"  Query successful. User found: {user is not None}")
        except Exception as e:
            print(f"⚠️  Error querying user by email: {str(e)[:200]}...")
            traceback.print_exc()
            _safe_rollback(db)
            raise

        if user:
            print(f"✓ Admin user already exists: {user.email}")
        else:
            print(f"  Creating new admin user: {ADMIN_EMAIL}")
            try:
                user = repo.create_user(email=ADMIN_EMAIL, password=ADMIN_PASSWORD)
                print(f"  User created with id={user.id}")
                user.is_active = True
                user.is_verified = True
                db.flush()
                print(f"✓ Admin user created and activated: {user.email}")
            except Exception as e:
                print(f"⚠️  Error creating user: {str(e)[:200]}...")
                traceback.print_exc()
                _safe_rollback(db)
                raise

        # ── 3. Ensure admin has a UserProfile linked to the company ───────────────────
        if company_id is not None:
            print("\n📋 Step 3: Creating admin profile...")
            try:
                print(f"  Querying UserProfile for user_id={user.id}...")
                profile = db.query(UserProfile).filter_by(user_id=user.id).first()
                print(f"  Query successful. Profile found: {profile is not None}")
            except Exception as e:
                print(f"⚠️  Error querying UserProfile: {str(e)[:200]}...")
                traceback.print_exc()
                _safe_rollback(db)
                raise

            if profile:
                print(f"✓ Admin profile already exists: {profile.full_name}")
            else:
                print(f"  Creating UserProfile...")
                print(f"    - user_id: {user.id}")
                print(f"    - company_id: {company_id}")
                print(f"    - role: {UserRole.SUPER_ADMIN.value}")
                try:
                    profile = UserProfile(
                        user_id=user.id,
                        company_id=company_id,
                        role=UserRole.SUPER_ADMIN.value,  # Use string value
                        first_name="Super",
                        last_name="Admin",
                    )
                    print(f"  UserProfile object created")
                    db.add(profile)
                    print(f"  Added to session, flushing...")
                    db.flush()
                    print(f"✓ Admin profile created (Super Admin) with id={profile.id}")
                except Exception as e:
                    print(f"⚠️  Error creating UserProfile: {str(e)[:200]}...")
                    traceback.print_exc()
                    _safe_rollback(db)
                    raise
        else:
            print("\n📋 Step 3: Skipping UserProfile creation (company not available)")

        print(f"\n📋 Step 4: Committing transaction...")
        db.commit()
        print(f"✓ Transaction committed successfully")

        print("")
        print("─" * 40)
        print("  Default login credentials")
        print(f"  Email   : {ADMIN_EMAIL}")
        print(f"  Password: {ADMIN_PASSWORD}")
        print("─" * 40)
        print("✅ Admin user initialization completed!")
        print("")

    except Exception as e:
        print(f"\n❌ Admin user initialization failed!")
        print(f"Error: {str(e)[:300]}...")
        db.rollback()
        sys.exit(1)

    finally:
        db.close()
        print("Database session closed.")


if __name__ == "__main__":
    main()
