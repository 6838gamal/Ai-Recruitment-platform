"""CRM module repositories."""
from sqlalchemy.orm import Session
from app.core.base.repository import BaseRepository
from app.modules.crm.models import Client


class ClientRepository(BaseRepository[Client]):
    def __init__(self, db: Session):
        super().__init__(Client, db)
