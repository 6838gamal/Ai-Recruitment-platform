"""AI Matching module repositories."""
from sqlalchemy.orm import Session
from app.modules.ai_matching.models import MatchResult


class MatchResultRepository:
    def __init__(self, db: Session):
        self.db = db
