"""Jobs module repositories."""
import uuid
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.core.base.repository import BaseRepository
from app.modules.jobs.models import JobPosting


class JobPostingRepository(BaseRepository):
    """Repository for JobPosting model."""

    def __init__(self, db: Session):
        super().__init__(JobPosting, db)

    def get_by_company(
        self,
        company_id: uuid.UUID,
        skip: int = 0,
        limit: int = 25,
        status: Optional[str] = None,
    ) -> List[JobPosting]:
        """Get jobs for a company with optional status filter."""
        query = self.db.query(JobPosting).filter(
            JobPosting.company_id == company_id,
            JobPosting.deleted_at.is_(None),
        )
        if status:
            query = query.filter(JobPosting.status == status)
        return query.offset(skip).limit(limit).all()

    def count_by_company(self, company_id: uuid.UUID, status: Optional[str] = None) -> int:
        """Count total jobs for a company."""
        query = self.db.query(JobPosting).filter(
            JobPosting.company_id == company_id,
            JobPosting.deleted_at.is_(None),
        )
        if status:
            query = query.filter(JobPosting.status == status)
        return query.count()

    def get_by_id(
        self,
        job_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> Optional[JobPosting]:
        """Get a job by ID and company (scoped access)."""
        return self.db.query(JobPosting).filter(
            JobPosting.id == job_id,
            JobPosting.company_id == company_id,
            JobPosting.deleted_at.is_(None),
        ).first()

    def get_by_id_only(self, job_id: uuid.UUID) -> Optional[JobPosting]:
        """Get a job by ID without company filter (admin use)."""
        return self.db.query(JobPosting).filter(
            JobPosting.id == job_id,
            JobPosting.deleted_at.is_(None),
        ).first()
