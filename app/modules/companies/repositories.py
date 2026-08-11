
"""Companies module repositories."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.base.repository import BaseRepository
from app.modules.companies.models import Company


class CompanyRepository(BaseRepository[Company]):
    """Repository for company database operations."""

    def __init__(self, db: Session):
        super().__init__(Company, db)

    def get_by_slug(self, slug: str) -> Optional[Company]:
        """Get an active company by slug."""

        stmt = select(Company).where(
            Company.slug == slug,
            Company.deleted_at.is_(None),
        )

        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, data: dict) -> Company:
        """
        Create and persist a company.

        This method explicitly commits the transaction so that
        the newly created company is immediately available when
        the user is redirected to the companies list.
        """

        company = Company(**data)

        self.db.add(company)

        try:
            self.db.commit()
            self.db.refresh(company)

            return company

        except Exception:
            self.db.rollback()
            raise

    def update(self, company: Company, data: dict) -> Company:
        """
        Update and persist a company.
        """

        for key, value in data.items():
            if hasattr(company, key):
                setattr(company, key, value)

        try:
            self.db.commit()
            self.db.refresh(company)

            return company

        except Exception:
            self.db.rollback()
            raise

    def soft_delete(self, company: Company) -> Company:
        """
        Soft-delete a company.
        """

        from datetime import datetime, timezone

        company.deleted_at = datetime.now(timezone.utc)

        try:
            self.db.commit()
            self.db.refresh(company)

            return company

        except Exception:
            self.db.rollback()
            raise
