"""Interviews module models."""
import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base.model import BaseModel, utcnow
from app.database import Base


class Interview(Base, BaseModel):
    __tablename__ = "interviews"

    application_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    interview_type: Mapped[str] = mapped_column(String(50), nullable=False)  # phone, video, in_person, technical
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_min: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="scheduled")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)

    evaluations = relationship("InterviewEvaluation", back_populates="interview", cascade="all, delete-orphan")


class InterviewEvaluation(Base, BaseModel):
    __tablename__ = "interview_evaluations"

    interview_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("interviews.id"), nullable=False)
    evaluator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    recommendation: Mapped[str] = mapped_column(String(50), nullable=False)  # hire, no_hire, consider
    strengths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weaknesses: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    interview = relationship("Interview", back_populates="evaluations")
