"""Reports module schemas."""
from typing import Optional
from datetime import date
from app.core.base.schema import BaseSchema


class ReportFilter(BaseSchema):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    company_id: Optional[str] = None
    department_id: Optional[str] = None
