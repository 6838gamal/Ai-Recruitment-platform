"""Base Pydantic schemas."""
import uuid
from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,        # Allow ORM model conversion
        populate_by_name=True,       # Allow both alias and field name
        str_strip_whitespace=True,   # Auto-strip whitespace
        use_enum_values=True,        # Use enum values in serialization
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""
    created_at: datetime
    updated_at: datetime


class UUIDSchema(BaseSchema):
    """Schema with UUID id field."""
    id: uuid.UUID


class BaseResponseSchema(UUIDSchema, TimestampSchema):
    """Full response schema with id and timestamps."""
    pass


# ─── Pagination ───────────────────────────────────────────────────────────────

T = TypeVar("T")


class PaginationMeta(BaseSchema):
    """Pagination metadata."""
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response."""
    items: List[T]
    meta: PaginationMeta


def make_pagination_meta(page: int, per_page: int, total: int) -> PaginationMeta:
    """Create pagination metadata."""
    total_pages = max(1, (total + per_page - 1) // per_page)
    return PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


# ─── API Response Wrapper ─────────────────────────────────────────────────────

class SuccessResponse(BaseSchema, Generic[T]):
    """Standard success response wrapper."""
    success: bool = True
    data: T


class ErrorDetail(BaseSchema):
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseSchema):
    """Standard error response."""
    success: bool = False
    error: dict
