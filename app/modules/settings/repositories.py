"""Settings module repositories."""
from sqlalchemy.orm import Session
from app.modules.settings.models import CompanySettings


class CompanySettingsRepository:
    def __init__(self, db: Session):
        self.db = db
