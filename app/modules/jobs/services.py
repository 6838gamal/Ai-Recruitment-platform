"""Jobs module services."""
from sqlalchemy.orm import Session
from sqlalchemy import select
from decimal import Decimal
import uuid
from typing import List, Optional, Tuple

from app.core.base.service import BaseService
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.modules.jobs.models import JobPosting
from app.modules.jobs.repositories import JobPostingRepository
from app.modules.jobs.schemas import JobPostingCreate, JobPostingUpdate


class JobService(BaseService):
    """Job management service."""

    def __init__(self, db: Session):
        super().__init__(db)
        self.repo = JobPostingRepository(db)

    def list_jobs(
        self,
        company_id: uuid.UUID,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 25,
    ) -> Tuple[List[JobPosting], int]:
        """List jobs for a company with pagination."""
        skip = (page - 1) * per_page
        jobs = self.repo.get_by_company(
            company_id=company_id,
            status=status,
            skip=skip,
            limit=per_page,
        )
        total = self.repo.count_by_company(company_id, status=status)
        return jobs, total

    def get_all_jobs(
        self,
        company_id: uuid.UUID,
        skip: int = 0,
        limit: int = 25,
    ) -> List[JobPosting]:
        """Get all jobs for a company with pagination."""
        return self.repo.get_by_company(
            company_id=company_id,
            skip=skip,
            limit=limit,
        )

    def get_job_by_id(
        self,
        job_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> Optional[JobPosting]:
        """Get a single job by ID (company-scoped)."""
        return self.repo.get_by_id(job_id, company_id)

    def create_job(
        self,
        current_user,
        data: dict,
    ) -> JobPosting:
        """Create a JobPosting from form/API data.

        Expects either current_user.company_id or data['company_id'] to be present.
        """
        company_id = getattr(current_user, "company_id", None) or data.get("company_id")
        if not company_id:
            raise ValueError("company_id is required to create a job")

        created_by = getattr(current_user, "id", None)
        if not created_by:
            raise PermissionDeniedError("Current user must have an ID")

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
        self.db.flush()
        return job

    def update_job(
        self,
        job_id: uuid.UUID,
        company_id: uuid.UUID,
        data: dict,
    ) -> JobPosting:
        """Update an existing job posting."""
        job = self.repo.get_by_id(job_id, company_id)
        if not job:
            raise NotFoundError("JobPosting", job_id)

        # Convert salary fields to Decimal when present
        if "salary_min" in data and data["salary_min"] is not None:
            data["salary_min"] = Decimal(str(data["salary_min"])) if data["salary_min"] != "" else None
        if "salary_max" in data and data["salary_max"] is not None:
            data["salary_max"] = Decimal(str(data["salary_max"])) if data["salary_max"] != "" else None

        updated = self.repo.update(job, data)
        self.db.commit()
        return updated

    def delete_job(
        self,
        job_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> JobPosting:
        """Soft-delete a job posting."""
        job = self.repo.get_by_id(job_id, company_id)
        if not job:
            raise NotFoundError("JobPosting", job_id)

        deleted = self.repo.soft_delete(job)
        self.db.commit()
        return deleted
