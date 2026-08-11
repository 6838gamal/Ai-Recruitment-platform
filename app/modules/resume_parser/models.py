"""Resume Parser module database models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    Float,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ParsedResume(Base):
    """Store uploaded and parsed resumes."""

    __tablename__ = "parsed_resumes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ------------------------------------------------------------------
    # File information
    # ------------------------------------------------------------------

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    file_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    file_size: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Parsing status
    # ------------------------------------------------------------------

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="uploaded",
        index=True,
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    parse_time: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Extracted personal information
    # ------------------------------------------------------------------

    first_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    last_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Extracted resume data
    # ------------------------------------------------------------------

    skills: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    experience: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    education: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    certifications: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    languages: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    years_of_experience: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    # ------------------------------------------------------------------
    # Raw extracted text
    # ------------------------------------------------------------------

    resume_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Matching information
    # ------------------------------------------------------------------

    matches: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    best_match_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    # ------------------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    parsed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def full_name(self) -> str:
        """Return the parsed candidate's full name."""

        return (
            f"{self.first_name or ''} "
            f"{self.last_name or ''}"
        ).strip()

    @property
    def is_completed(self) -> bool:
        """Return True when parsing completed successfully."""

        return self.status == "completed"

    @property
    def match_count(self) -> int:
        """Return the number of matching candidates."""

        if not self.matches:
            return 0

        return len(self.matches)

    def __repr__(self) -> str:
        return (
            f"<ParsedResume "
            f"id={self.id!r} "
            f"filename={self.filename!r} "
            f"status={self.status!r}>"
        )
