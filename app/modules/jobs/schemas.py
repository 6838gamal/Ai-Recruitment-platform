"""Jobs module Pydantic schemas."""
import uuid
from typing import Optional
from decimal import Decimal

from pydantic import Field

from app.core.base.schema import BaseResponseSchema, BaseSchema


class JobPostingCreate(BaseSchema):
    """Create a new job posting."""
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    employment_type: Optional[str] = Field(None, max_length=50)
    work_type: Optional[str] = Field(None, max_length=50)
    experience_min: Optional[int] = Field(None, ge=0)
    experience_max: Optional[int] = Field(None, ge=0)
    salary_min: Optional[Decimal] = Field(None, decimal_places=2)
    salary_max: Optional[Decimal] = Field(None, decimal_places=2)
    salary_currency: str = Field(default="USD", max_length=10)
    status: str = Field(default="draft", max_length=50)
    headcount: int = Field(default=1, ge=1)
    department_id: Optional[uuid.UUID] = None
    branch_id: Optional[uuid.UUID] = None


class JobPostingUpdate(BaseSchema):
    """Update an existing job posting."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    employment_type: Optional[str] = Field(None, max_length=50)
    work_type: Optional[str] = Field(None, max_length=50)
    experience_min: Optional[int] = Field(None, ge=0)
    experience_max: Optional[int] = Field(None, ge=0)
    salary_min: Optional[Decimal] = Field(None, decimal_places=2)
    salary_max: Optional[Decimal] = Field(None, decimal_places=2)
    salary_currency: Optional[str] = Field(None, max_length=10)
    status: Optional[str] = Field(None, max_length=50)
    headcount: Optional[int] = Field(None, ge=1)
    department_id: Optional[uuid.UUID] = None
    branch_id: Optional[uuid.UUID] = None


class JobPostingResponse(BaseResponseSchema):
    """Job posting response schema."""
    company_id: uuid.UUID
    branch_id: Optional[uuid.UUID]
    department_id: Optional[uuid.UUID]
    created_by_id: uuid.UUID
    title: str
    description: str
    requirements: Optional[str]
    responsibilities: Optional[str]
    employment_type: Optional[str]
    work_type: Optional[str]
    experience_min: Optional[int]
    experience_max: Optional[int]
    salary_min: Optional[Decimal]
    salary_max: Optional[Decimal]
    salary_currency: str
    status: str
    headcount: int


class JobListItem(BaseSchema):
    """Compact job item for list views."""
    id: uuid.UUID
    title: str
    status: str
    employment_type: Optional[str]
    salary_min: Optional[Decimal]
    salary_max: Optional[Decimal]
    salary_currency: str
    headcount: int
