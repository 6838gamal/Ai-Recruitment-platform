"""Base repository with generic CRUD operations."""
import uuid
from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.base.model import BaseModel
from app.core.base.schema import PaginationMeta, make_pagination_meta
from app.database import Base

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository providing standard CRUD operations.
    Subclass this for each module's repository.
    """

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    # ─── Read ──────────────────────────────────────────────────────────────

    def get_by_id(self, id: uuid.UUID, include_deleted: bool = False) -> Optional[ModelType]:
        """Get a single record by ID."""
        stmt = select(self.model).where(self.model.id == id)
        if not include_deleted:
            stmt = stmt.where(self.model.deleted_at.is_(None))
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 25,
        include_deleted: bool = False,
    ) -> List[ModelType]:
        """Get all records with optional pagination."""
        stmt = select(self.model)
        if not include_deleted:
            stmt = stmt.where(self.model.deleted_at.is_(None))
        stmt = stmt.offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count(self, include_deleted: bool = False) -> int:
        """Count all records."""
        stmt = select(func.count()).select_from(self.model)
        if not include_deleted:
            stmt = stmt.where(self.model.deleted_at.is_(None))
        return self.db.execute(stmt).scalar_one()

    def paginate(
        self,
        page: int = 1,
        per_page: int = 25,
        include_deleted: bool = False,
        **filters: Any,
    ) -> tuple[List[ModelType], PaginationMeta]:
        """Paginate results with metadata."""
        skip = (page - 1) * per_page

        stmt = select(self.model)
        if not include_deleted:
            stmt = stmt.where(self.model.deleted_at.is_(None))

        # Apply simple equality filters
        for field, value in filters.items():
            if value is not None and hasattr(self.model, field):
                stmt = stmt.where(getattr(self.model, field) == value)

        # Count query
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        # Data query
        items = list(self.db.execute(stmt.offset(skip).limit(per_page)).scalars().all())
        meta = make_pagination_meta(page=page, per_page=per_page, total=total)

        return items, meta

    # ─── Write ─────────────────────────────────────────────────────────────

    def create(self, data: dict[str, Any]) -> ModelType:
        """Create a new record."""
        instance = self.model(**data)
        self.db.add(instance)
        self.db.flush()  # Get id without committing
        self.db.refresh(instance)
        return instance

    def update(self, instance: ModelType, data: dict[str, Any]) -> ModelType:
        """Update an existing record."""
        for field, value in data.items():
            if hasattr(instance, field) and value is not None:
                setattr(instance, field, value)
        self.db.flush()
        self.db.refresh(instance)
        return instance

    def soft_delete(self, instance: ModelType) -> ModelType:
        """Soft-delete a record (sets deleted_at)."""
        instance.soft_delete()
        self.db.flush()
        return instance

    def hard_delete(self, instance: ModelType) -> None:
        """Permanently delete a record from the database."""
        self.db.delete(instance)
        self.db.flush()

    def save(self) -> None:
        """Commit the current transaction."""
        self.db.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.db.rollback()
