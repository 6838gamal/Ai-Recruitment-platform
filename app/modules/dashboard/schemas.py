"""Dashboard module schemas."""
from app.core.base.schema import BaseSchema


class DashboardStats(BaseSchema):
    total_jobs: int = 0
    active_jobs: int = 0
    total_candidates: int = 0
    new_candidates_this_week: int = 0
    total_applications: int = 0
    interviews_today: int = 0
    hired_this_month: int = 0
