"""Jobs module repositories."""
from sqlalchemy.orm import Session
from app.core.base.repository import BaseRepository
from app.modules.jobs.models import JobPosting


class JobRepository(BaseRepository[JobPosting]):
    def __init__(self, db: Session):
        super().__init__(JobPosting, db)
