"""Resume Parser module services."""
import io
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.base.service import BaseService
from app.modules.resume_parser.schemas import ParsedResume
from app.modules.candidates.models import Candidate


class ResumeParserService(BaseService):
    """Service for parsing resumes from PDF/DOCX/images."""

    def __init__(self, db: Session = None):
        if db:
            super().__init__(db)
            self.db = db

    def parse_pdf(self, file_bytes: bytes) -> ParsedResume:
        """Extract text from PDF and parse into structured data."""
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return self._parse_text(text)
        except Exception as e:
            return ParsedResume(confidence_score=0.0)

    def parse_docx(self, file_bytes: bytes) -> ParsedResume:
        """Extract text from DOCX and parse into structured data."""
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            text = "\n".join(para.text for para in doc.paragraphs)
            return self._parse_text(text)
        except Exception as e:
            return ParsedResume(confidence_score=0.0)

    def _parse_text(self, text: str) -> ParsedResume:
        """
        Parse raw resume text into structured data.
        TODO: Integrate AI provider for advanced extraction.
        Currently uses basic regex patterns.
        """
        import re

        result = ParsedResume()

        # Basic email extraction
        email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', text)
        if email_match:
            result.email = email_match.group()

        # Basic phone extraction
        phone_match = re.search(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
        if phone_match:
            result.phone = phone_match.group()

        result.confidence_score = 0.5 if result.email else 0.2
        return result

    def get_parsed_resumes(self, company_id, page: int = 1, per_page: int = 25):
        """Get list of parsed resumes for a company."""
        if not self.db:
            return [], 0
            
        query = self.db.query(Candidate).filter(Candidate.company_id == company_id)
        total = query.count()
        
        candidates = query.order_by(desc(Candidate.created_at)).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        return candidates, total

    def get_parsed_resume_by_id(self, resume_id, company_id) -> Optional[Candidate]:
        """Get a specific parsed resume."""
        if not self.db:
            return None
            
        return self.db.query(Candidate).filter(
            Candidate.id == resume_id,
            Candidate.company_id == company_id
        ).first()
