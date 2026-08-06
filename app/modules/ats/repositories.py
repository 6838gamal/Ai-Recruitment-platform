"""ATS module repositories."""
from sqlalchemy.orm import Session
from app.core.base.repository import BaseRepository
from app.modules.ats.models import Application


class ApplicationRepository(BaseRepository[Application]):
    def __init__(self, db: Session):
        super().__init__(Application, db)
