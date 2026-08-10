"""Jobs module services."""
from sqlalchemy.orm import Session
from sqlalchemy import select
from decimal import Decimal
import uuid

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

    def create_job(self, current_user, data: dict) -> JobPosting:
        """Create a JobPosting from form/API data.

        Expects either current_user.company_id or data['company_id'] to be present.
        """
        company_id = getattr(current_user, "company_id", None) or data.get("company_id")
        if not company_id:
            raise ValueError("company_id is required to create a job")

        created_by = getattr(current_user, "id", None)

        # Convert salary fields to Decimal when present
        salary_min = data.get("salary_min")
        salary_max = data.get("salary_max")
        salary_min = Decimal(str(salary_min)) if salary_min is not None and salary_min != "" else None
        salary_max = Decimal(str(salary_max)) if salary_max is not None and salary_max != "" else None

        job = JobPosting(
            company_id=company_id,
            created_by_id=created_by,
            title=data.get("title") or "",
            description=data.get("description") or "",
            requirements=data.get("requirements"),
            responsibilities=data.get("responsibilities"),
            employment_type=data.get("employment_type"),
            work_type=data.get("work_type"),
            experience_min=data.get("experience_min"),
            experience_max=data.get("experience_max"),
            salary_min=salary_min,
            salary_max=salary_max,
            salary_currency=data.get("salary_currency", "USD"),
            status=data.get("status", "draft"),
            headcount=data.get("headcount") or 1,
            department_id=data.get("department_id"),
            branch_id=data.get("branch_id"),
        )

        self.db.add(job)
        # Flush so the job gets an id populated before commit
        self.db.flush()
        return job
