"""Candidates module repositories."""
from sqlalchemy.orm import Session
from app.core.base.repository import BaseRepository
from app.modules.candidates.models import Candidate


class CandidateRepository(BaseRepository[Candidate]):
    def __init__(self, db: Session):
        super().__init__(Candidate, db)
