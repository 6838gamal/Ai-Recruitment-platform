"""Jobs module SQLAlchemy models."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base.model import BaseModel
from app.database import Base


class JobPosting(Base, BaseModel):
    """Job posting model."""

    __tablename__ = "job_postings"

    # ============================================================
    # BASIC RELATIONSHIPS
    # ============================================================

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "companies.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    branch_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "branches.id",
        ),
        nullable=True,
    )

    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "departments.id",
        ),
        nullable=True,
    )

    # IMPORTANT:
    # The database migration says this references
    # user_profiles.id, NOT users.id.
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_profiles.id",
        ),
        nullable=False,
    )

    # ============================================================
    # JOB INFORMATION
    # ============================================================

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    requirements: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    responsibilities: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    employment_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    work_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    # ============================================================
    # EXPERIENCE
    # ============================================================

    experience_min: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    experience_max: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # ============================================================
    # SALARY
    # ============================================================

    salary_min: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    salary_max: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    salary_currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="USD",
        server_default="USD",
    )

    # ============================================================
    # STATUS
    # ============================================================

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft",
        server_default="draft",
        index=True,
    )

    # ============================================================
    # EXPIRATION
    # ============================================================

    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ============================================================
    # HEADCOUNT
    # ============================================================

    headcount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    # ============================================================
    # RELATIONSHIPS
    # ============================================================

    company = relationship(
        "Company",
        lazy="select",
    )

    branch = relationship(
        "Branch",
        lazy="select",
    )

    department = relationship(
        "Department",
        lazy="select",
    )

    created_by = relationship(
        "UserProfile",
        foreign_keys=[created_by_id],
        lazy="select",
    )

    # ============================================================
    # REPRESENTATION
    # ============================================================

    def __repr__(self) -> str:
        return (
            f"<JobPosting "
            f"title={self.title!r} "
            f"id={self.id}>"
        )
