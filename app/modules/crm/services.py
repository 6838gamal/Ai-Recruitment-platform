"""CRM module services."""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.base.service import BaseService
from app.modules.crm.models import Client, ClientContact


class CRMService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.db = db

    def create_client(self, company_id, data: dict) -> Client:
        """Create a new client."""
        client = Client(
            company_id=company_id,
            name=data.get("name"),
            industry=data.get("industry"),
            website=data.get("website"),
            status=data.get("status", "active"),
            notes=data.get("notes"),
        )
        self.db.add(client)
        self.db.flush()
        return client

    def get_client_by_id(self, client_id, company_id) -> Client:
        """Get a client by ID."""
        return self.db.query(Client).filter(
            Client.id == client_id,
            Client.company_id == company_id
        ).first()

    def list_clients(self, company_id, page: int = 1, per_page: int = 25):
        """List all clients for a company."""
        query = self.db.query(Client).filter(Client.company_id == company_id)
        total = query.count()
        
        clients = query.order_by(desc(Client.created_at)).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        return clients, total

    def update_client(self, client_id, company_id, data: dict) -> Client:
        """Update a client."""
        client = self.get_client_by_id(client_id, company_id)
        if not client:
            raise Exception("Client not found")
        
        for key, value in data.items():
            if hasattr(client, key) and value is not None:
                setattr(client, key, value)
        
        self.db.flush()
        return client

    def delete_client(self, client_id, company_id):
        """Delete a client."""
        client = self.get_client_by_id(client_id, company_id)
        if not client:
            raise Exception("Client not found")
        
        self.db.delete(client)
        self.db.flush()

    def create_contact(self, client_id, data: dict) -> ClientContact:
        """Create a new contact for a client."""
        contact = ClientContact(
            client_id=client_id,
            full_name=data.get("full_name"),
            email=data.get("email"),
            phone=data.get("phone"),
            job_title=data.get("job_title"),
            is_primary=data.get("is_primary", False),
        )
        self.db.add(contact)
        self.db.flush()
        return contact

    def get_contact_by_id(self, contact_id) -> ClientContact:
        """Get a contact by ID."""
        return self.db.query(ClientContact).filter(
            ClientContact.id == contact_id
        ).first()

    def update_contact(self, contact_id, data: dict) -> ClientContact:
        """Update a contact."""
        contact = self.get_contact_by_id(contact_id)
        if not contact:
            raise Exception("Contact not found")
        
        for key, value in data.items():
            if hasattr(contact, key) and value is not None:
                setattr(contact, key, value)
        
        self.db.flush()
        return contact

    def delete_contact(self, contact_id):
        """Delete a contact."""
        contact = self.get_contact_by_id(contact_id)
        if not contact:
            raise Exception("Contact not found")
        
        self.db.delete(contact)
        self.db.flush()
