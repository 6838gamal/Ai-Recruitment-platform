"""Accounts module business logic."""
from datetime import timedelta
from typing import Optional, Tuple

from fastapi import BackgroundTasks, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.core.base.service import BaseService
from app.core.exceptions import (
    AccountLockedError,
    AuthenticationError,
    InvalidTokenError,
    NotFoundError,
    ValidationError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_secure_token,
    hash_token,
    verify_password,
)
from app.modules.accounts.models import User
from app.modules.accounts.repositories import (
    PasswordResetTokenRepository,
    RefreshTokenRepository,
    UserRepository,
)
from app.modules.accounts.schemas import (
    ChangePasswordSchema,
    ForgotPasswordSchema,
    LoginSchema,
    ResetPasswordSchema,
)


class AuthService(BaseService):
    """Authentication service — login, logout, tokens, password reset."""

    def __init__(self, db: Session):
        super().__init__(db)
        self.user_repo = UserRepository(db)
        self.refresh_repo = RefreshTokenRepository(db)
        self.reset_repo = PasswordResetTokenRepository(db)

    def login(
        self,
        data: LoginSchema,
        request: Optional[Request] = None,
    ) -> Tuple[str, str, User]:
        """
        Authenticate user. Returns (access_token, refresh_token, user).
        Raises AuthenticationError, AccountLockedError on failure.
        """
        user = self.user_repo.get_by_email(data.email)

        # User not found — use same error message to prevent user enumeration
        if not user:
            raise AuthenticationError("Invalid email or password")

        # Check account lockout
        if self.user_repo.is_locked(user):
            raise AccountLockedError("Account is temporarily locked. Try again later.")

        # Check active status
        if not user.is_active:
            raise AuthenticationError("Account is deactivated. Contact support.")

        # Verify password
        if not verify_password(data.password, user.hashed_password):
            self.user_repo.increment_failed_attempts(user)
            self.db.commit()
            raise AuthenticationError("Invalid email or password")

        # Successful login — reset failed attempts
        self.user_repo.reset_failed_attempts(user)

        # Create tokens
        token_data = {"sub": str(user.id)}
        access_token = create_access_token(token_data)
        refresh_token = generate_secure_token(32)

        # Store hashed refresh token
        ip_address = request.client.host if request and request.client else None
        user_agent = request.headers.get("user-agent") if request else None
        self.refresh_repo.create(
            user_id=user.id,
            raw_token=refresh_token,
            expires_in_days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.commit()

        return access_token, refresh_token, user

    def logout(self, raw_refresh_token: str) -> None:
        """Revoke the given refresh token."""
        token_hash = hash_token(raw_refresh_token)
        token = self.refresh_repo.get_by_token_hash(token_hash)
        if token:
            self.refresh_repo.revoke(token)
            self.db.commit()

    def refresh_access_token(self, raw_refresh_token: str) -> Tuple[str, str]:
        """
        Rotate refresh token and issue new access + refresh tokens.
        Returns (new_access_token, new_refresh_token).
        """
        token_hash = hash_token(raw_refresh_token)
        stored_token = self.refresh_repo.get_by_token_hash(token_hash)

        if not stored_token:
            raise InvalidTokenError("Invalid or expired refresh token")

        user = self.user_repo.get_by_id(stored_token.user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")

        # Revoke old refresh token (rotation)
        self.refresh_repo.revoke(stored_token)

        # Issue new tokens
        token_data = {"sub": str(user.id)}
        new_access_token = create_access_token(token_data)
        new_refresh_token = generate_secure_token(32)

        self.refresh_repo.create(
            user_id=user.id,
            raw_token=new_refresh_token,
            expires_in_days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
        )
        self.db.commit()

        return new_access_token, new_refresh_token

    def initiate_password_reset(
        self,
        data: ForgotPasswordSchema,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        """
        Generate and send a password reset token.
        Always succeeds (no user enumeration via response).
        """
        user = self.user_repo.get_by_email(data.email)
        if not user:
            return  # Silent fail — don't reveal user existence

        raw_token = generate_secure_token(32)
        self.reset_repo.create(user_id=user.id, raw_token=raw_token)
        self.db.commit()

        # Send email in background
        if background_tasks:
            background_tasks.add_task(
                self._send_reset_email,
                email=user.email,
                token=raw_token,
            )

    def _send_reset_email(self, email: str, token: str) -> None:
        """Background task: send password reset email."""
        # TODO: Implement via notifications module
        reset_url = f"/auth/reset-password?token={token}"
        print(f"[EMAIL] Password reset for {email}: {reset_url}")

    def reset_password(self, data: ResetPasswordSchema) -> None:
        """Apply a password reset using a valid token."""
        token_hash = hash_token(data.token)
        stored_token = self.reset_repo.get_valid_token(token_hash)

        if not stored_token:
            raise InvalidTokenError("Invalid or expired reset token")

        user = self.user_repo.get_by_id(stored_token.user_id)
        if not user:
            raise NotFoundError("User")

        self.user_repo.update_password(user, data.new_password)
        self.reset_repo.mark_used(stored_token)
        # Revoke all active sessions after password change
        self.refresh_repo.revoke_all_for_user(user.id)
        self.db.commit()

    def change_password(self, user: User, data: ChangePasswordSchema) -> None:
        """Change password for an authenticated user."""
        if not verify_password(data.current_password, user.hashed_password):
            raise ValidationError("Current password is incorrect", field="current_password")

        self.user_repo.update_password(user, data.new_password)
        # Revoke all other sessions
        self.refresh_repo.revoke_all_for_user(user.id)
        self.db.commit()
