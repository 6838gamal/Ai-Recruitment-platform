"""Base service class."""
from sqlalchemy.orm import Session


class BaseService:
    """
    Base service class providing access to the database session.
    Subclass this for each module's service.
    """

    def __init__(self, db: Session):
        self.db = db
