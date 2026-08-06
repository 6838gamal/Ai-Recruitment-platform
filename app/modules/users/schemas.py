"""Users module Pydantic schemas."""
import uuid
from typing import Optional

from pydantic import EmailStr, Field

from app.core.base.schema import BaseResponseSchema, BaseSchema
from app.core.permissions import UserRole


class UserProfileCreate(BaseSchema):
    """Create a new user + profile."""
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    role: UserRole
    company_id: uuid.UUID
    branch_id: Optional[uuid.UUID] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None


class UserProfileUpdate(BaseSchema):
    """Update an existing user profile."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    branch_id: Optional[uuid.UUID] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None


class UserProfileResponse(BaseResponseSchema):
    """User profile response schema."""
    user_id: uuid.UUID
    company_id: uuid.UUID
    branch_id: Optional[uuid.UUID]
    role: str
    first_name: str
    last_name: str
    full_name: str
    phone: Optional[str]
    avatar_url: Optional[str]
    job_title: Optional[str]
    department: Optional[str]
    email: Optional[str] = None  # populated from user relationship


class UserListItem(BaseSchema):
    """Compact user item for list views."""
    id: uuid.UUID
    full_name: str
    role: str
    job_title: Optional[str]
    department: Optional[str]
    avatar_url: Optional[str]
