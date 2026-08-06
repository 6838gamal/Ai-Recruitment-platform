"""Interviews module repositories."""
from sqlalchemy.orm import Session
from app.core.base.repository import BaseRepository
from app.modules.interviews.models import Interview


class InterviewRepository(BaseRepository[Interview]):
    def __init__(self, db: Session):
        super().__init__(Interview, db)
