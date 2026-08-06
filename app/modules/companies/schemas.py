"""Companies module schemas."""
from typing import Optional
from app.core.base.schema import BaseResponseSchema, BaseSchema


class CompanyCreate(BaseSchema):
    name: str
    slug: str
    website: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    timezone: str = "UTC"


class CompanyUpdate(BaseSchema):
    name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    logo_url: Optional[str] = None


class CompanyResponse(BaseResponseSchema):
    name: str
    slug: str
    logo_url: Optional[str]
    industry: Optional[str]
    country: Optional[str]
    timezone: str
    is_active: bool
