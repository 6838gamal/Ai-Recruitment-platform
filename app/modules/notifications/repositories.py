"""Notifications module repositories."""
from sqlalchemy.orm import Session
from app.modules.notifications.models import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db
