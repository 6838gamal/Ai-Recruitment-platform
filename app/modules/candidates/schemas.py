"""Candidates module schemas."""
from typing import Optional
from app.core.base.schema import BaseResponseSchema, BaseSchema


class CandidateCreate(BaseSchema):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None
    summary: Optional[str] = None


class CandidateResponse(BaseResponseSchema):
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone: Optional[str]
    status: str
    source: Optional[str]
    avatar_url: Optional[str]
