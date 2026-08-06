"""Resume Parser module schemas."""
from typing import List, Optional
from app.core.base.schema import BaseSchema


class ParsedExperience(BaseSchema):
    company_name: str
    job_title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class ParsedEducation(BaseSchema):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None


class ParsedResume(BaseSchema):
    """Structured data extracted from a resume."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = []
    experiences: List[ParsedExperience] = []
    education: List[ParsedEducation] = []
    languages: List[str] = []
    confidence_score: float = 0.0
