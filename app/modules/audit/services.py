"""Audit module services."""
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.modules.audit.models import AuditLog


class AuditService:
    """Service for logging audit events."""

    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        action: str,
        user_id: Optional[uuid.UUID] = None,
        company_id: Optional[uuid.UUID] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[uuid.UUID] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
    ) -> AuditLog:
        """Create an audit log entry."""
        log = AuditLog(
            action=action,
            user_id=user_id,
            company_id=company_id,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
        )
        self.db.add(log)
        self.db.flush()
        return log
