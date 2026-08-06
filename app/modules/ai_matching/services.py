"""AI Matching module services."""
from sqlalchemy.orm import Session
from app.core.base.service import BaseService


class AIMatchingService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)
