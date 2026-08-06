"""Accounts module repositories."""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.base.repository import BaseRepository
from app.core.security import hash_password, hash_token
from app.modules.accounts.models import PasswordResetToken, RefreshToken, User


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """Find an active user by email address."""
        stmt = select(User).where(
            User.email == email.lower().strip(),
            User.deleted_at.is_(None),
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create_user(self, email: str, password: str) -> User:
        """Create a new user with hashed password."""
        return self.create({
            "email": email.lower().strip(),
            "hashed_password": hash_password(password),
        })

    def increment_failed_attempts(self, user: User, max_attempts: int = 5) -> User:
        """Increment failed login attempts, locking if threshold reached."""
        user.failed_attempts += 1
        if user.failed_attempts >= max_attempts:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
        self.db.flush()
        return user

    def reset_failed_attempts(self, user: User) -> User:
        """Reset failed attempts and lockout after successful login."""
        user.failed_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(timezone.utc)
        self.db.flush()
        return user

    def update_password(self, user: User, new_password: str) -> User:
        """Update user's password hash."""
        user.hashed_password = hash_password(new_password)
        self.db.flush()
        return user

    def is_locked(self, user: User) -> bool:
        """Check if user account is locked."""
        if user.locked_until is None:
            return False
        return datetime.now(timezone.utc) < user.locked_until


class RefreshTokenRepository:
    """Repository for RefreshToken model."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: uuid.UUID,
        raw_token: str,
        expires_in_days: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> RefreshToken:
        """Store a hashed refresh token."""
        token = RefreshToken(
            user_id=user_id,
            token_hash=hash_token(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=expires_in_days),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(token)
        self.db.flush()
        return token

    def get_by_token_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """Find a refresh token by its SHA-256 hash."""
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked.is_(False),
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def revoke(self, token: RefreshToken) -> None:
        """Revoke a specific refresh token."""
        token.is_revoked = True
        self.db.flush()

    def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        """Revoke all refresh tokens for a user (e.g., after token theft)."""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.is_revoked.is_(False))
            .values(is_revoked=True)
        )
        self.db.execute(stmt)
        self.db.flush()


class PasswordResetTokenRepository:
    """Repository for PasswordResetToken model."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: uuid.UUID, raw_token: str, expires_in_hours: int = 1) -> PasswordResetToken:
        """Store a hashed password reset token."""
        token = PasswordResetToken(
            user_id=user_id,
            token_hash=hash_token(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=expires_in_hours),
        )
        self.db.add(token)
        self.db.flush()
        return token

    def get_valid_token(self, token_hash: str) -> Optional[PasswordResetToken]:
        """Find a valid (unused, unexpired) reset token."""
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.is_used.is_(False),
            PasswordResetToken.expires_at > datetime.now(timezone.utc),
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def mark_used(self, token: PasswordResetToken) -> None:
        """Mark reset token as used."""
        token.is_used = True
        self.db.flush()
