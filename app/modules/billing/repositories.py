"""Billing module repositories."""
from sqlalchemy.orm import Session
from app.core.base.repository import BaseRepository
from app.modules.billing.models import Invoice


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, db: Session):
        super().__init__(Invoice, db)
