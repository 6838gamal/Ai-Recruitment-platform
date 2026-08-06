"""Notifications module services."""
from sqlalchemy.orm import Session
from app.core.base.service import BaseService


class NotificationService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    def send_in_app(self, user_id, title: str, message: str, type: str = "info", action_url: str = None):
        """Create an in-app notification."""
        from app.modules.notifications.models import Notification
        import uuid
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            action_url=action_url,
        )
        self.db.add(notification)
        self.db.flush()
        return notification
