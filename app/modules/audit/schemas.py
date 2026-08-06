"""Audit module schemas."""
import uuid
from typing import Optional
from datetime import datetime
from app.core.base.schema import BaseSchema


class AuditLogResponse(BaseSchema):
    id: uuid.UUID
    action: str
    entity_type: Optional[str]
    status: str
    ip_address: Optional[str]
    created_at: datetime
