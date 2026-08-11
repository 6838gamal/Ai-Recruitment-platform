"""Users module SQLAlchemy models."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base.model import BaseModel, TimestampMixin, utcnow
from app.database import Base


class UserProfile(Base, BaseModel):
    """User profile — extended user information per company."""

    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    branch_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="user")
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    user = relationship("User", back_populates="profile")
    company = relationship("Company", back_populates="user_profiles")

    @property
    def full_name(self) -> str:
        """Return full name of the user."""
        parts = [self.first_name or "", self.last_name or ""]
        return " ".join(p for p in parts if p).strip() or "Unknown"

    def __repr__(self) -> str:
        return f"<UserProfile user_id={self.user_id} role={self.role}>"
