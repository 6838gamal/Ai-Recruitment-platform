
"""Users module SQLAlchemy models."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base.model import BaseModel, TimestampMixin


class User(BaseModel, TimestampMixin):
    """
    Application user.

    Maps to the existing `users` database table.

    This model intentionally contains only fields that exist
    in the current Alembic users table.
    """

    __tablename__ = "users"

    # ========================================================================
    # Authentication
    # ========================================================================

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # ========================================================================
    # Account status
    # ========================================================================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # ========================================================================
    # Login information
    # ========================================================================

    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ========================================================================
    # Security / account locking
    # ========================================================================

    failed_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ========================================================================
    # Identity
    # ========================================================================

    # `id`, `created_at`, `updated_at`, and `deleted_at`
    # are inherited from BaseModel / TimestampMixin.
