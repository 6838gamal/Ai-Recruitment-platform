"""Settings module schemas."""
from typing import Optional
from app.core.base.schema import BaseSchema


class CompanySettingsUpdate(BaseSchema):
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_use_tls: Optional[bool] = None
    from_email: Optional[str] = None
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    storage_backend: Optional[str] = None


class CompanySettingsResponse(BaseSchema):
    smtp_host: Optional[str]
    smtp_port: Optional[int]
    smtp_username: Optional[str]
    smtp_use_tls: bool
    from_email: Optional[str]
    ai_provider: Optional[str]
    storage_backend: str
