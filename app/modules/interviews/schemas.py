"""Interviews module schemas."""
from typing import Optional
from datetime import datetime
import uuid

from app.core.base.schema import BaseResponseSchema, BaseSchema


class InterviewCreate(BaseSchema):
    application_id: uuid.UUID
    interview_type: str
    scheduled_at: datetime
    duration_min: int = 60
    location: Optional[str] = None


class InterviewResponse(BaseResponseSchema):
    application_id: uuid.UUID
    interview_type: str
    scheduled_at: datetime
    status: str
