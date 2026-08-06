"""Dashboard module services."""
from sqlalchemy.orm import Session

from app.core.base.service import BaseService
from app.modules.dashboard.schemas import DashboardStats


class DashboardService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    def get_stats(self, company_id) -> DashboardStats:
        """Aggregate statistics for the dashboard."""
        from sqlalchemy import func, select
        from app.modules.jobs.models import JobPosting
        from app.modules.candidates.models import Candidate
        from app.modules.ats.models import Application

        try:
            total_jobs = self.db.execute(
                select(func.count()).select_from(JobPosting).where(
                    JobPosting.company_id == company_id,
                    JobPosting.deleted_at.is_(None)
                )
            ).scalar_one()

            active_jobs = self.db.execute(
                select(func.count()).select_from(JobPosting).where(
                    JobPosting.company_id == company_id,
                    JobPosting.status == "active",
                    JobPosting.deleted_at.is_(None)
                )
            ).scalar_one()

            total_candidates = self.db.execute(
                select(func.count()).select_from(Candidate).where(
                    Candidate.company_id == company_id,
                    Candidate.deleted_at.is_(None)
                )
            ).scalar_one()

            return DashboardStats(
                total_jobs=total_jobs,
                active_jobs=active_jobs,
                total_candidates=total_candidates,
            )
        except Exception:
            return DashboardStats()
