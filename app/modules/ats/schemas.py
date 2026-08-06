"""ATS module schemas."""
import uuid
from typing import Optional
from app.core.base.schema import BaseResponseSchema, BaseSchema

ATS_STAGES = ["applied", "screening", "shortlisted", "interview", "technical", "hr_interview", "offer", "hired", "rejected"]


class ApplicationCreate(BaseSchema):
    job_id: uuid.UUID
    candidate_id: uuid.UUID


class StageMove(BaseSchema):
    stage: str
    note: Optional[str] = None


class ApplicationResponse(BaseResponseSchema):
    job_id: uuid.UUID
    candidate_id: uuid.UUID
    stage: str
