"""Notifications module schemas."""
import uuid
from typing import Optional
from datetime import datetime
from app.core.base.schema import BaseSchema


class NotificationResponse(BaseSchema):
    id: uuid.UUID
    title: str
    message: str
    type: str
    is_read: bool
    action_url: Optional[str]
    created_at: datetime
