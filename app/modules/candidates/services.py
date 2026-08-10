"""Candidates module services."""
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.core.base.service import BaseService
from app.modules.candidates.models import Candidate


class CandidateService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    def get_all_candidates(self, company_id, skip: int = 0, limit: int = 25):
        """Get all candidates for a company with pagination and total count."""
        stmt = select(Candidate).where(
            Candidate.company_id == company_id,
            Candidate.deleted_at.is_(None),
        ).offset(skip).limit(limit)

        candidates = self.db.execute(stmt).scalars().all()

        # total count
        count_stmt = select(func.count()).select_from(Candidate).where(
            Candidate.company_id == company_id,
            Candidate.deleted_at.is_(None),
        )
        total = self.db.execute(count_stmt).scalar_one()
        return candidates, total

    def get_candidate_by_id(self, candidate_id, company_id):
        """Get a single candidate by ID."""
        stmt = select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.company_id == company_id,
            Candidate.deleted_at.is_(None),
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create_candidate(self, company_id, first_name, last_name, email, **kwargs):
        """Create and persist a Candidate, returning the created instance."""
        candidate = Candidate(
            company_id=company_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            **kwargs,
        )
        try:
            self.db.add(candidate)
            self.db.commit()
            self.db.refresh(candidate)
            return candidate
        except Exception:
            self.db.rollback()
            raise
