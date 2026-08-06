"""Users module repositories."""
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.base.repository import BaseRepository
from app.modules.users.models import UserProfile


class UserProfileRepository(BaseRepository[UserProfile]):
    """Repository for UserProfile model."""

    def __init__(self, db: Session):
        super().__init__(UserProfile, db)

    def get_by_user_id(self, user_id: uuid.UUID) -> Optional[UserProfile]:
        """Find profile by auth user UUID."""
        stmt = (
            select(UserProfile)
            .options(joinedload(UserProfile.user))
            .where(
                UserProfile.user_id == user_id,
                UserProfile.deleted_at.is_(None),
            )
        )
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def get_by_company(
        self,
        company_id: uuid.UUID,
        role: Optional[str] = None,
        skip: int = 0,
        limit: int = 25,
    ) -> List[UserProfile]:
        """List user profiles for a company, optionally filtered by role."""
        stmt = (
            select(UserProfile)
            .options(joinedload(UserProfile.user))
            .where(
                UserProfile.company_id == company_id,
                UserProfile.deleted_at.is_(None),
            )
        )
        if role:
            stmt = stmt.where(UserProfile.role == role)
        stmt = stmt.offset(skip).limit(limit)
        return list(self.db.execute(stmt).unique().scalars().all())

    def count_by_company(self, company_id: uuid.UUID) -> int:
        """Count active users in a company."""
        from sqlalchemy import func
        stmt = select(func.count()).select_from(UserProfile).where(
            UserProfile.company_id == company_id,
            UserProfile.deleted_at.is_(None),
        )
        return self.db.execute(stmt).scalar_one()
