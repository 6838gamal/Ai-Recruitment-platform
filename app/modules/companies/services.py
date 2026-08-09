from sqlalchemy.orm import Session
from app.core.base.service import BaseService
from app.modules.companies.repositories import CompanyRepository
from app.modules.companies.models import Company
from typing import List, Optional
import uuid


class CompanyService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.repo = CompanyRepository(db)

    def list_companies(self, skip: int = 0, limit: int = 25) -> List[Company]:
        return self.repo.get_all(skip=skip, limit=limit)

    def get_by_slug(self, slug: str) -> Optional[Company]:
        return self.repo.get_by_slug(slug)

    def get_by_id(self, id: uuid.UUID) -> Optional[Company]:
        return self.repo.get_by_id(id)

    def create_company(self, data: dict) -> Company:
        return self.repo.create(data)

    def update_company(self, company: Company, data: dict) -> Company:
        return self.repo.update(company, data)
