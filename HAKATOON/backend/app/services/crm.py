from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.prospect import Prospect


class CRMService:
    def get_or_create_customer(self, db: Session, phone: str, name: str | None) -> Customer:
        existing = db.scalar(select(Customer).where(Customer.phone == phone))
        if existing is not None:
            if name and existing.name != name:
                existing.name = name
                db.add(existing)
                db.commit()
            return existing
        customer = Customer(name=name or "Prospect", phone=phone, hectares=0.0, total_spent=0.0, purchases_count=0)
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    def get_or_create_prospect(self, db: Session, customer_id: int) -> Prospect:
        prospect = db.scalar(select(Prospect).where(Prospect.customer_id == customer_id))
        if prospect is not None:
            return prospect
        prospect = Prospect(customer_id=customer_id, status="new", lead_score=0.0)
        db.add(prospect)
        db.commit()
        db.refresh(prospect)
        return prospect

    def update_prospect_status(self, db: Session, customer_id: int, status: str, last_intent: str | None) -> Prospect:
        prospect = self.get_or_create_prospect(db, customer_id=customer_id)
        prospect.status = status
        prospect.last_intent = last_intent
        prospect.updated_at = datetime.utcnow()
        db.add(prospect)
        db.commit()
        db.refresh(prospect)
        return prospect


crm_service = CRMService()
