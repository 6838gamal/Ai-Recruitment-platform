"""Audit module repositories."""
from sqlalchemy.orm import Session
from app.modules.audit.models import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db
