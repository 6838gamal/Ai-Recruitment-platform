"""Companies module repositories."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.base.repository import BaseRepository
from app.modules.companies.models import Company


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, db: Session):
        super().__init__(Company, db)

    def get_by_slug(self, slug: str) -> Optional[Company]:
        stmt = select(Company).where(Company.slug == slug, Company.deleted_at.is_(None))
        return self.db.execute(stmt).scalar_one_or_none()
