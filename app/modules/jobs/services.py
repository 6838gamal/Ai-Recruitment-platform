"""Jobs module services."""
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.base.service import BaseService
from app.modules.jobs.models import JobPosting


class JobService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    def get_all_jobs(self, company_id, skip: int = 0, limit: int = 25):
        """Get all jobs for a company with pagination."""
        stmt = select(JobPosting).where(
            JobPosting.company_id == company_id,
            JobPosting.deleted_at.is_(None)
        ).offset(skip).limit(limit)
        
        jobs = self.db.execute(stmt).scalars().all()
        return jobs

    def get_job_by_id(self, job_id, company_id):
        """Get a single job by ID."""
        stmt = select(JobPosting).where(
            JobPosting.id == job_id,
            JobPosting.company_id == company_id,
            JobPosting.deleted_at.is_(None)
        )
        return self.db.execute(stmt).scalar_one_or_none()
