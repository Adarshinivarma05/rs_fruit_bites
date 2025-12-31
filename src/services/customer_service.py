"""Customer service for business logic."""
from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from src.repositories.customer_repository import CustomerRepository
from src.repositories.audit_repository import AuditRepository


class CustomerService:
    """Service for customer business logic."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.customer_repo = CustomerRepository(db)
        self.audit_repo = AuditRepository(db)

    def create_customer(
        self,
        name: str,
        area: str = "",
        mobile: str = "",
        subscription: str = "Basic",
        custom_rate: float = 0.0,
    ) -> dict:
        """Create a new customer with validation."""
        existing = self.customer_repo.get_by_name(name)
        if existing:
            raise ValueError(f"Customer '{name}' already exists")

        customer = self.customer_repo.create(
            name=name,
            area=area,
            mobile=mobile,
            subscription=subscription,
            custom_rate=custom_rate,
        )

        self.audit_repo.log_action("ADD_CUSTOMER", f"Added customer: {name}")
        self.db.commit()

        return {
            "id": customer.id,
            "name": customer.name,
            "area": customer.area,
            "mobile": customer.mobile,
            "subscription": customer.subscription,
            "custom_rate": customer.custom_rate,
            "status": customer.status,
        }

    def get_all_customers(self, active_only: bool = True) -> List[dict]:
        """Get all customers."""
        customers = self.customer_repo.get_all(active_only=active_only)
        return [
            {
                "id": c.id,
                "name": c.name,
                "area": c.area or "",
                "mobile": c.mobile or "",
                "subscription": c.subscription,
                "custom_rate": c.custom_rate,
                "start_date": c.start_date.isoformat() if c.start_date else None,
                "end_date": c.end_date.isoformat() if c.end_date else None,
                "status": c.status,
            }
            for c in customers
        ]

    def get_inactive_customers(self) -> List[dict]:
        """Get all inactive customers."""
        customers = self.customer_repo.get_inactive()
        return [
            {
                "id": c.id,
                "name": c.name,
                "area": c.area or "",
                "mobile": c.mobile or "",
                "subscription": c.subscription,
                "custom_rate": c.custom_rate,
                "start_date": c.start_date.isoformat() if c.start_date else None,
                "end_date": c.end_date.isoformat() if c.end_date else None,
                "status": c.status,
            }
            for c in customers
        ]

    def update_customer(
        self,
        name: str,
        area: Optional[str] = None,
        mobile: Optional[str] = None,
        subscription: Optional[str] = None,
        custom_rate: Optional[float] = None,
    ) -> dict:
        """Update customer details."""
        customer = self.customer_repo.get_by_name(name)
        if not customer:
            raise ValueError(f"Customer '{name}' not found")

        customer = self.customer_repo.update(
            customer=customer,
            area=area,
            mobile=mobile,
            subscription=subscription,
            custom_rate=custom_rate,
        )

        self.audit_repo.log_action("UPDATE_CUSTOMER", f"Updated customer: {name}")
        self.db.commit()

        return {
            "id": customer.id,
            "name": customer.name,
            "area": customer.area,
            "mobile": customer.mobile,
            "subscription": customer.subscription,
            "custom_rate": customer.custom_rate,
        }

    def deactivate_customer(self, name: str) -> None:
        """Deactivate a customer (soft delete)."""
        customer = self.customer_repo.get_by_name(name)
        if not customer:
            raise ValueError(f"Customer '{name}' not found")

        self.customer_repo.deactivate(customer)
        self.audit_repo.log_action("DEACTIVATE_CUSTOMER", f"Deactivated customer: {name}")
        self.db.commit()

    def reactivate_customer(self, name: str) -> None:
        """Reactivate an inactive customer."""
        customer = self.customer_repo.get_by_name(name)
        if not customer:
            raise ValueError(f"Customer '{name}' not found")

        self.customer_repo.reactivate(customer)
        self.audit_repo.log_action("REACTIVATE_CUSTOMER", f"Reactivated customer: {name}")
        self.db.commit()

    def delete_customer_permanently(self, name: str, reason: str = "") -> None:
        """Permanently delete a customer with audit logging."""
        customer = self.customer_repo.get_by_name(name)
        if not customer:
            raise ValueError(f"Customer '{name}' not found")

        self.audit_repo.log_deleted_member(customer, reason)
        self.audit_repo.log_action(
            "DELETE_CUSTOMER", f"Permanently deleted customer: {name} - Reason: {reason}"
        )
        self.customer_repo.delete(customer)
        self.db.commit()

    def extend_end_date(self, name: str, days: int = 1) -> None:
        """Extend customer's end date by specified days."""
        customer = self.customer_repo.get_by_name(name)
        if not customer:
            return

        if customer.end_date:
            from datetime import timedelta
            new_end_date = customer.end_date + timedelta(days=days)
        else:
            from datetime import timedelta
            new_end_date = date.today() + timedelta(days=30 + days)

        self.customer_repo.update(customer=customer, end_date=new_end_date)
        self.db.commit()
