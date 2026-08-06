"""Files module repositories."""
from sqlalchemy.orm import Session
from app.modules.files.models import FileUpload


class FileUploadRepository:
    def __init__(self, db: Session):
        self.db = db
