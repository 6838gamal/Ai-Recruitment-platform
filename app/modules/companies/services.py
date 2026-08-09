"""Companies module services."""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.base.service import BaseService
from app.modules.companies.models import Company


class CompanyService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)
    
    def list_companies(self, skip: int = 0, limit: int = 100, is_active: bool = None):
        """Get list of companies with optional filtering."""
        query = self.db.query(Company)
        
        if is_active is not None:
            query = query.filter(Company.is_active == is_active)
        
        return query.order_by(desc(Company.created_at)).offset(skip).limit(limit).all()
    
    def get_company_by_id(self, company_id: str):
        """Get a single company by ID."""
        return self.db.query(Company).filter(Company.id == company_id).first()
    
    def get_company_by_slug(self, slug: str):
        """Get a company by its slug."""
        return self.db.query(Company).filter(Company.slug == slug).first()
    
    def create_company(self, name: str, slug: str, **kwargs):
        """Create a new company."""
        company = Company(name=name, slug=slug, **kwargs)
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company
    
    def update_company(self, company_id: str, **kwargs):
        """Update an existing company."""
        company = self.get_company_by_id(company_id)
        if not company:
            return None
        
        for key, value in kwargs.items():
            if hasattr(company, key):
                setattr(company, key, value)
        
        self.db.commit()
        self.db.refresh(company)
        return company
    
    def delete_company(self, company_id: str):
        """Delete a company."""
        company = self.get_company_by_id(company_id)
        if not company:
            return False
        
        self.db.delete(company)
        self.db.commit()
        return True
    
    def toggle_company_status(self, company_id: str):
        """Toggle company active status."""
        company = self.get_company_by_id(company_id)
        if not company:
            return None
        
        company.is_active = not company.is_active
        self.db.commit()
        self.db.refresh(company)
        return company
    
    def get_company_statistics(self):
        """Get company statistics."""
        total = self.db.query(Company).count()
        active = self.db.query(Company).filter(Company.is_active == True).count()
        inactive = total - active
        
        return {
            "total": total,
            "active": active,
            "inactive": inactive,
        }
