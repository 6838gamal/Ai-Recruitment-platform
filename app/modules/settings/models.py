"""Settings module models."""
import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base.model import utcnow
from app.database import Base


class CompanySettings(Base):
    __tablename__ = "company_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), unique=True, nullable=False)
    smtp_host: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    smtp_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=587)
    smtp_username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    smtp_password: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    smtp_use_tls: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    from_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ai_provider: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="openai")
    ai_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ai_api_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    storage_backend: Mapped[str] = mapped_column(String(50), nullable=False, default="local")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
