"""Accounts module Pydantic schemas."""
import re
import uuid
from typing import Optional

from pydantic import EmailStr, Field, field_validator, model_validator

from app.core.base.schema import BaseSchema


# ─── Login ────────────────────────────────────────────────────────────────────

class LoginSchema(BaseSchema):
    """Login request schema."""
    email: EmailStr
    password: str = Field(min_length=1)
    remember_me: bool = False


class TokenResponse(BaseSchema):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


# ─── Password ─────────────────────────────────────────────────────────────────

PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_\-#])[A-Za-z\d@$!%*?&_\-#]{8,}$"
)


def validate_password_strength(password: str) -> str:
    """Validate password meets security requirements."""
    if not PASSWORD_REGEX.match(password):
        raise ValueError(
            "Password must be at least 8 characters and contain uppercase, "
            "lowercase, digit, and special character (@$!%*?&_-#)"
        )
    return password


class ChangePasswordSchema(BaseSchema):
    """Change password request schema."""
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return validate_password_strength(v)

    @model_validator(mode="after")
    def passwords_match(self) -> "ChangePasswordSchema":
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class ForgotPasswordSchema(BaseSchema):
    """Forgot password request schema."""
    email: EmailStr


class ResetPasswordSchema(BaseSchema):
    """Reset password request schema."""
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return validate_password_strength(v)

    @model_validator(mode="after")
    def passwords_match(self) -> "ResetPasswordSchema":
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


# ─── User Response ────────────────────────────────────────────────────────────

class UserResponse(BaseSchema):
    """Basic user response (auth identity only)."""
    id: uuid.UUID
    email: str
    is_active: bool
    is_verified: bool
