from app.database import SessionLocal
from app.modules.accounts.repositories import UserRepository


EMAIL = "admin@admin.com"
PASSWORD = "Admin@1234"


def main():
    db = SessionLocal()

    try:
        repo = UserRepository(db)

        user = repo.get_by_email(EMAIL)

        if user:
            print(f"✓ Admin user already exists: {user.email}")
            return

        user = repo.create_user(
            email=EMAIL,
            password=PASSWORD,
        )

        user.is_active = True
        user.is_verified = True

        db.commit()

        print("✓ Admin user created successfully")
        print(f"  Email: {EMAIL}")
        print(f"  Password: {PASSWORD}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
