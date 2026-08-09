"""Dashboard module services."""
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from datetime import datetime, timedelta

from app.core.base.service import BaseService
from app.modules.dashboard.schemas import DashboardStats


class DashboardService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    def get_stats(self, company_id) -> DashboardStats:
        """Aggregate statistics for the dashboard."""
        from app.modules.jobs.models import JobPosting
        from app.modules.candidates.models import Candidate

        try:
            active_jobs = self.db.execute(
                select(func.count()).select_from(JobPosting).where(
                    JobPosting.company_id == company_id,
                    JobPosting.status == "active",
                    JobPosting.deleted_at.is_(None)
                )
            ).scalar_one() or 0

            total_candidates = self.db.execute(
                select(func.count()).select_from(Candidate).where(
                    Candidate.company_id == company_id,
                    Candidate.deleted_at.is_(None)
                )
            ).scalar_one() or 0

            # Try to get pending applications count
            pending_applications = 0
            scheduled_interviews = 0
            
            try:
                from app.modules.ats.models import Application
                pending_applications = self.db.execute(
                    select(func.count()).select_from(Application).where(
                        Application.company_id == company_id,
                        Application.status == "pending",
                        Application.deleted_at.is_(None)
                    )
                ).scalar_one() or 0
            except:
                pass

            try:
                from app.modules.interviews.models import Interview
                scheduled_interviews = self.db.execute(
                    select(func.count()).select_from(Interview).where(
                        Interview.company_id == company_id,
                        Interview.scheduled_at > datetime.utcnow(),
                        Interview.deleted_at.is_(None)
                    )
                ).scalar_one() or 0
            except:
                pass

            return DashboardStats(
                active_jobs=active_jobs,
                total_candidates=total_candidates,
                pending_applications=pending_applications,
                scheduled_interviews=scheduled_interviews,
            )
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return DashboardStats(
                active_jobs=0,
                total_candidates=0,
                pending_applications=0,
                scheduled_interviews=0,
            )

    def get_recent_activities(self, company_id, limit: int = 5):
        """Get recent activities for the dashboard."""
        from app.modules.jobs.models import JobPosting

        activities = []

        try:
            # Recent jobs posted
            recent_jobs = self.db.execute(
                select(JobPosting)
                .where(
                    JobPosting.company_id == company_id,
                    JobPosting.deleted_at.is_(None),
                )
                .order_by(JobPosting.created_at.desc())
                .limit(2)
            ).scalars().all()

            for job in recent_jobs:
                activities.append({
                    "type": "job_posted",
                    "title": "New job posted",
                    "description": f"{job.title} role",
                    "time_ago": self._format_time_ago(job.created_at),
                })

            # Recent applications
            try:
                from app.modules.ats.models import Application
                recent_apps = self.db.execute(
                    select(Application)
                    .where(
                        Application.company_id == company_id,
                        Application.deleted_at.is_(None),
                    )
                    .order_by(Application.created_at.desc())
                    .limit(2)
                ).scalars().all()

                for app in recent_apps:
                    activities.append({
                        "type": "application_received",
                        "title": "Application received",
                        "description": f"New application submitted",
                        "time_ago": self._format_time_ago(app.created_at),
                    })
            except:
                pass

            # Recent interviews
            try:
                from app.modules.interviews.models import Interview
                recent_interviews = self.db.execute(
                    select(Interview)
                    .where(
                        Interview.company_id == company_id,
                        Interview.deleted_at.is_(None),
                    )
                    .order_by(Interview.created_at.desc())
                    .limit(1)
                ).scalars().all()

                for interview in recent_interviews:
                    activities.append({
                        "type": "interview_scheduled",
                        "title": "Interview scheduled",
                        "description": f"Scheduled for {interview.scheduled_at.strftime('%Y-%m-%d') if interview.scheduled_at else 'TBD'}",
                        "time_ago": self._format_time_ago(interview.created_at),
                    })
            except:
                pass

            # Sort by time and return limited results
            return sorted(activities, key=lambda x: x["time_ago"])[:limit]

        except Exception as e:
            print(f"Error getting recent activities: {e}")
            return []

    @staticmethod
    def _format_time_ago(dt: datetime) -> str:
        """Format datetime as 'time ago' string."""
        if not dt:
            return "unknown"

        now = datetime.utcnow()
        diff = now - dt

        if diff.days > 0:
            if diff.days == 1:
                return "1 day ago"
            return f"{diff.days} days ago"

        hours = diff.seconds // 3600
        if hours > 0:
            if hours == 1:
                return "1 hour ago"
            return f"{hours} hours ago"

        minutes = diff.seconds // 60
        if minutes > 0:
            if minutes == 1:
                return "1 minute ago"
            return f"{minutes} minutes ago"

        return "just now"
