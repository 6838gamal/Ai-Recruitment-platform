```python
"""Candidates module services."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.base.service import BaseService
from app.modules.candidates.models import Candidate


class CandidateService(BaseService):
    """Service for candidate operations."""

    def __init__(self, db: Session):
        super().__init__(db)

    def get_candidates(
        self,
        company_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Candidate]:
        """Get candidates for a company."""

        return (
            self.db.query(Candidate)
            .filter(
                Candidate.company_id == company_id,
            )
            .order_by(Candidate.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_candidate(
        self,
        candidate_id: UUID,
        company_id: UUID,
    ) -> Candidate | None:
        """Get a single candidate."""

        return (
            self.db.query(Candidate)
            .filter(
                Candidate.id == candidate_id,
                Candidate.company_id == company_id,
            )
            .first()
        )

    def create_candidate(
        self,
        company_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        phone: str | None = None,
        location: str | None = None,
        linkedin_url: str | None = None,
        portfolio_url: str | None = None,
        summary: str | None = None,
        status: str = "new",
        source: str | None = None,
        avatar_url: str | None = None,
    ) -> Candidate:
        """Create a new candidate."""

        candidate = Candidate(
            company_id=company_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            location=location,
            linkedin_url=linkedin_url,
            portfolio_url=portfolio_url,
            summary=summary,
            status=status or "new",
            source=source,
            avatar_url=avatar_url,
        )

        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)

        return candidate

    def update_candidate(
        self,
        candidate_id: UUID,
        company_id: UUID,
        **data,
    ) -> Candidate | None:
        """Update an existing candidate."""

        candidate = self.get_candidate(
            candidate_id=candidate_id,
            company_id=company_id,
        )

        if not candidate:
            return None

        allowed_fields = {
            "first_name",
            "last_name",
            "email",
            "phone",
            "location",
            "linkedin_url",
            "portfolio_url",
            "summary",
            "status",
            "source",
            "avatar_url",
        }

        for field, value in data.items():
            if field in allowed_fields:
                setattr(candidate, field, value)

        self.db.commit()
        self.db.refresh(candidate)

        return candidate

    def delete_candidate(
        self,
        candidate_id: UUID,
        company_id: UUID,
    ) -> bool:
        """Delete a candidate."""

        candidate = self.get_candidate(
            candidate_id=candidate_id,
            company_id=company_id,
        )

        if not candidate:
            return False

        self.db.delete(candidate)
        self.db.commit()

        return True
```
