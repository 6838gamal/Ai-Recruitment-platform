"""Candidates module services."""
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.base.service import BaseService
from app.modules.candidates.models import Candidate


class CandidateService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    def get_all_candidates(self, company_id, skip: int = 0, limit: int = 25):
        """Get all candidates for a company with pagination."""
        stmt = select(Candidate).where(
            Candidate.company_id == company_id,
            Candidate.deleted_at.is_(None)
        ).offset(skip).limit(limit)
        
        candidates = self.db.execute(stmt).scalars().all()
        return candidates

    def get_candidate_by_id(self, candidate_id, company_id):
        """Get a single candidate by ID."""
        stmt = select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.company_id == company_id,
            Candidate.deleted_at.is_(None)
        )
        return self.db.execute(stmt).scalar_one_or_none()
