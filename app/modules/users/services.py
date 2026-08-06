"""Users module business logic."""
import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.base.service import BaseService
from app.core.exceptions import AlreadyExistsError, NotFoundError, PermissionDeniedError
from app.core.permissions import UserRole, has_min_role
from app.modules.accounts.repositories import UserRepository
from app.modules.accounts.models import User
from app.modules.users.models import UserProfile
from app.modules.users.repositories import UserProfileRepository
from app.modules.users.schemas import UserProfileCreate, UserProfileUpdate


class UserService(BaseService):
    """User management service."""

    def __init__(self, db: Session):
        super().__init__(db)
        self.profile_repo = UserProfileRepository(db)
        self.user_repo = UserRepository(db)

    def create_user(
        self,
        data: UserProfileCreate,
        created_by: Optional[UserProfile] = None,
    ) -> UserProfile:
        """Create a new user with profile."""
        # Permission check: can't create user with higher role
        if created_by and created_by.role != UserRole.SUPER_ADMIN.value:
            if not has_min_role(UserRole(created_by.role), UserRole(data.role)):
                raise PermissionDeniedError("Cannot assign a role higher than your own")

        # Check email uniqueness
        existing = self.user_repo.get_by_email(data.email)
        if existing:
            raise AlreadyExistsError("User", "email")

        # Create auth user
        from app.core.security import hash_password
        user = self.user_repo.create({
            "email": data.email.lower().strip(),
            "hashed_password": hash_password(data.password),
        })

        # Create profile
        profile = self.profile_repo.create({
            "user_id": user.id,
            "company_id": data.company_id,
            "branch_id": data.branch_id,
            "role": data.role.value if hasattr(data.role, 'value') else data.role,
            "first_name": data.first_name,
            "last_name": data.last_name,
            "phone": data.phone,
            "job_title": data.job_title,
            "department": data.department,
        })

        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update_profile(
        self,
        profile_id: uuid.UUID,
        data: UserProfileUpdate,
        updated_by: Optional[UserProfile] = None,
    ) -> UserProfile:
        """Update a user profile."""
        profile = self.profile_repo.get_by_id(profile_id)
        if not profile:
            raise NotFoundError("UserProfile", profile_id)

        update_data = data.model_dump(exclude_none=True)
        if "role" in update_data and isinstance(update_data["role"], UserRole):
            update_data["role"] = update_data["role"].value

        updated = self.profile_repo.update(profile, update_data)
        self.db.commit()
        return updated

    def deactivate_user(self, profile_id: uuid.UUID) -> UserProfile:
        """Soft-delete a user profile and deactivate auth user."""
        profile = self.profile_repo.get_by_id(profile_id)
        if not profile:
            raise NotFoundError("UserProfile", profile_id)

        # Deactivate auth user
        auth_user = self.user_repo.get_by_id(profile.user_id)
        if auth_user:
            auth_user.is_active = False

        self.profile_repo.soft_delete(profile)
        self.db.commit()
        return profile

    def list_users(
        self,
        company_id: uuid.UUID,
        role: Optional[str] = None,
        page: int = 1,
        per_page: int = 25,
    ) -> tuple[List[UserProfile], int]:
        """List users for a company."""
        skip = (page - 1) * per_page
        users = self.profile_repo.get_by_company(
            company_id=company_id,
            role=role,
            skip=skip,
            limit=per_page,
        )
        total = self.profile_repo.count_by_company(company_id)
        return users, total
