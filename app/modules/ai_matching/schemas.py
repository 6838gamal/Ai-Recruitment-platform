"""AI Matching module schemas."""
import uuid
from typing import List, Optional
from app.core.base.schema import BaseSchema


class MatchRequest(BaseSchema):
    job_id: uuid.UUID
    candidate_id: uuid.UUID


class MatchResultResponse(BaseSchema):
    job_id: uuid.UUID
    candidate_id: uuid.UUID
    score: float
    provider: str
    summary: Optional[str]
    strengths: Optional[List[str]]
    weaknesses: Optional[List[str]]
    missing_skills: Optional[List[str]]
