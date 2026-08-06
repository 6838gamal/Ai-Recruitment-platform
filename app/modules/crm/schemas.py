"""CRM module schemas."""
from typing import Optional
from app.core.base.schema import BaseResponseSchema, BaseSchema


class ClientCreate(BaseSchema):
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None


class ClientResponse(BaseResponseSchema):
    name: str
    industry: Optional[str]
    status: str
