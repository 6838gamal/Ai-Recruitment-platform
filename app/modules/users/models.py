
"""Job models."""

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.core.base.model import BaseModel


class JobPosting(Base, BaseModel):
    """Job posting model."""

    __tablename__ = "job_postings"

    # ========================================================================
    # Basic information
    # ========================================================================

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft",
    )

    # ========================================================================
    # Company
    # ========================================================================

    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "companies.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    company = relationship(
        "Company",
        lazy="select",
    )

    # ========================================================================
    # Creator
    # ========================================================================

    created_by_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    created_by = relationship(
        "User",
        lazy="select",
    )

    # ========================================================================
    # Representation
    # ========================================================================

    def __repr__(self) -> str:
        return (
            f"<JobPosting "
            f"title={self.title!r} "
            f"id={self.id}>"
        )
