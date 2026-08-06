"""Resume Parser module services."""
import io
from typing import Optional

from app.modules.resume_parser.schemas import ParsedResume


class ResumeParserService:
    """Service for parsing resumes from PDF/DOCX/images."""

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
