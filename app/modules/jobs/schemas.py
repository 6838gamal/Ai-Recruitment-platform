"""Jobs module schemas."""
from decimal import Decimal
from typing import Optional
from datetime import datetime
import uuid

from app.core.base.schema import BaseResponseSchema, BaseSchema


class JobCreate(BaseSchema):
    title: str
    description: str
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    employment_type: Optional[str] = None
    work_type: Optional[str] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    salary_currency: str = "USD"
    status: str = "draft"
    expires_at: Optional[datetime] = None
    headcount: int = 1
    department_id: Optional[uuid.UUID] = None
    branch_id: Optional[uuid.UUID] = None


class JobUpdate(BaseSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class JobResponse(BaseResponseSchema):
    title: str
    status: str
    employment_type: Optional[str]
    work_type: Optional[str]
    salary_min: Optional[Decimal]
    salary_max: Optional[Decimal]
    salary_currency: str
    headcount: int
