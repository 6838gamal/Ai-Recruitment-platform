"""Billing module schemas."""
from typing import Optional
from datetime import date
from app.core.base.schema import BaseResponseSchema, BaseSchema


class InvoiceResponse(BaseResponseSchema):
    invoice_number: str
    amount: float
    currency: str
    status: str
    due_date: date
