
"""Candidates module services."""

from __future__ import annotations

import re
from typing import Any
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.base.service import BaseService
from app.modules.candidates.models import Candidate


class CandidateService(BaseService):
    """Service for candidate operations."""

    def __init__(self, db: Session):
        super().__init__(db)

    # ================================================================
    # Candidate CRUD
    # ================================================================

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

    # ================================================================
    # Resume Matching
    # ================================================================

    @staticmethod
    def _normalize_text(value: Any) -> str:
        """Normalize text for matching."""

        if value is None:
            return ""

        if isinstance(value, (list, tuple, set)):
            value = " ".join(
                str(item)
                for item in value
                if item is not None
            )

        value = str(value).lower()

        value = re.sub(
            r"[^\w\s+#.-]",
            " ",
            value,
            flags=re.UNICODE,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    @classmethod
    def _candidate_text(
        cls,
        candidate: Candidate,
    ) -> str:
        """
        Build searchable text from a candidate.

        Only attributes that actually exist on the Candidate model
        are read. This keeps matching compatible with different
        candidate model versions.
        """

        values: list[str] = []

        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "location",
            "summary",
            "status",
            "source",
            "linkedin_url",
            "portfolio_url",
            "job_title",
            "title",
            "skills",
            "experience",
            "education",
            "certifications",
            "languages",
        )

        for field in fields:
            if hasattr(candidate, field):
                value = getattr(candidate, field, None)

                if value is not None:
                    values.append(
                        cls._normalize_text(value)
                    )

        return " ".join(
            value
            for value in values
            if value
        )

    @staticmethod
    def _resume_text(
        parsed_resume: dict[str, Any],
    ) -> str:
        """Build searchable text from parsed resume data."""

        values: list[str] = []

        fields = (
            "full_name",
            "first_name",
            "last_name",
            "email",
            "phone",
            "location",
            "title",
            "job_title",
            "summary",
            "skills",
            "experience",
            "education",
            "certifications",
            "languages",
            "resume_text",
        )

        for field in fields:
            value = parsed_resume.get(field)

            if value is None:
                continue

            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        values.extend(
                            str(v)
                            for v in item.values()
                            if v is not None
                        )
                    else:
                        values.append(str(item))
            else:
                values.append(str(value))

        return CandidateService._normalize_text(
            " ".join(values)
        )

    @staticmethod
    def _extract_resume_keywords(
        parsed_resume: dict[str, Any],
    ) -> set[str]:
        """Extract useful matching keywords from a parsed resume."""

        keywords: set[str] = set()

        def add_value(value: Any) -> None:
            if value is None:
                return

            if isinstance(value, (list, tuple, set)):
                for item in value:
                    add_value(item)
                return

            if isinstance(value, dict):
                for item in value.values():
                    add_value(item)
                return

            normalized = CandidateService._normalize_text(
                value
            )

            if not normalized:
                return

            words = normalized.split()

            for word in words:
                if len(word) >= 3:
                    keywords.add(word)

            # Keep multi-word values as phrases too.
            if len(words) > 1:
                keywords.add(normalized)

        # Skills are particularly important.
        add_value(
            parsed_resume.get("skills")
        )

        # Job title.
        add_value(
            parsed_resume.get("title")
        )

        add_value(
            parsed_resume.get("job_title")
        )

        # Education.
        add_value(
            parsed_resume.get("education")
        )

        # Experience.
        add_value(
            parsed_resume.get("experience")
        )

        # Languages.
        add_value(
            parsed_resume.get("languages")
        )

        # Certifications.
        add_value(
            parsed_resume.get("certifications")
        )

        return keywords

    @classmethod
    def _calculate_match_score(
        cls,
        parsed_resume: dict[str, Any],
        candidate: Candidate,
    ) -> float:
        """
        Calculate a simple resume-to-candidate similarity score.

        The score is intentionally deterministic and requires no
        external AI service.
        """

        resume_text = cls._resume_text(
            parsed_resume
        )

        candidate_text = cls._candidate_text(
            candidate
        )

        if not resume_text or not candidate_text:
            return 0.0

        resume_keywords = cls._extract_resume_keywords(
            parsed_resume
        )

        candidate_words = set(
            candidate_text.split()
        )

        score = 0.0

        # ------------------------------------------------------------
        # Keyword overlap
        # ------------------------------------------------------------

        if resume_keywords:
            matched_keywords = {
                keyword
                for keyword in resume_keywords
                if keyword in candidate_text
            }

            keyword_ratio = (
                len(matched_keywords)
                / len(resume_keywords)
            )

            score += keyword_ratio * 60.0

        # ------------------------------------------------------------
        # Job title similarity
        # ------------------------------------------------------------

        resume_title = cls._normalize_text(
            parsed_resume.get("job_title")
            or parsed_resume.get("title")
        )

        if resume_title:
            title_words = {
                word
                for word in resume_title.split()
                if len(word) >= 3
            }

            if title_words:
                matched_title_words = (
                    title_words.intersection(
                        candidate_words
                    )
                )

                title_ratio = (
                    len(matched_title_words)
                    / len(title_words)
                )

                score += title_ratio * 25.0

        # ------------------------------------------------------------
        # Location similarity
        # ------------------------------------------------------------

        resume_location = cls._normalize_text(
            parsed_resume.get("location")
        )

        candidate_location = cls._normalize_text(
            getattr(candidate, "location", None)
        )

        if (
            resume_location
            and candidate_location
            and (
                resume_location in candidate_location
                or candidate_location in resume_location
            )
        ):
            score += 10.0

        # ------------------------------------------------------------
        # Email similarity
        # ------------------------------------------------------------

        resume_email = cls._normalize_text(
            parsed_resume.get("email")
        )

        candidate_email = cls._normalize_text(
            getattr(candidate, "email", None)
        )

        if (
            resume_email
            and candidate_email
            and resume_email == candidate_email
        ):
            score += 5.0

        return round(
            min(score, 100.0),
            2,
        )

    def match_resume(
        self,
        parsed_resume: dict[str, Any],
        *,
        company_id: UUID | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Compare a parsed resume against existing candidates.

        This method is used by ResumeParserService.

        If company_id is provided, only candidates belonging to
        that company are considered. Otherwise all candidates are
        considered.
        """

        if not self.db:
            return []

        query = self.db.query(Candidate)

        if company_id is not None:
            query = query.filter(
                Candidate.company_id == company_id
            )

        candidates = (
            query
            .order_by(Candidate.created_at.desc())
            .limit(500)
            .all()
        )

        if not candidates:
            return []

        results: list[dict[str, Any]] = []

        for candidate in candidates:
            score = self._calculate_match_score(
                parsed_resume,
                candidate,
            )

            results.append(
                {
                    "candidate_id": str(candidate.id),
                    "first_name": getattr(
                        candidate,
                        "first_name",
                        None,
                    ),
                    "last_name": getattr(
                        candidate,
                        "last_name",
                        None,
                    ),
                    "full_name": (
                        f"{getattr(candidate, 'first_name', '') or ''} "
                        f"{getattr(candidate, 'last_name', '') or ''}"
                    ).strip(),
                    "email": getattr(
                        candidate,
                        "email",
                        None,
                    ),
                    "phone": getattr(
                        candidate,
                        "phone",
                        None,
                    ),
                    "location": getattr(
                        candidate,
                        "location",
                        None,
                    ),
                    "summary": getattr(
                        candidate,
                        "summary",
                        None,
                    ),
                    "match_score": score,
                }
            )

        results.sort(
            key=lambda item: item["match_score"],
            reverse=True,
        )

        return results[:limit]

