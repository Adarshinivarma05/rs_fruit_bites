"""Customer repository for database operations."""
from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.customer import Customer


class CustomerRepository:
    """Repository for customer database operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        name: str,
        area: str = "",
        mobile: str = "",
        subscription: str = "Basic",
        custom_rate: float = 0.0,
    ) -> Customer:
        """Create a new customer."""
        customer = Customer(
            name=name,
            area=area,
            mobile=mobile,
            subscription=subscription,
            custom_rate=custom_rate,
            status="active",
        )
        self.db.add(customer)
        self.db.flush()
        return customer

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID."""
        return self.db.get(Customer, customer_id)

    def get_by_name(self, name: str) -> Optional[Customer]:
        """Get customer by name."""
        stmt = select(Customer).where(Customer.name == name)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all(self, active_only: bool = True) -> List[Customer]:
        """Get all customers."""
        stmt = select(Customer)
        if active_only:
            stmt = stmt.where(Customer.status == "active")
        stmt = stmt.order_by(Customer.name)
        return list(self.db.execute(stmt).scalars().all())

    def get_inactive(self) -> List[Customer]:
        """Get all inactive customers."""
        stmt = select(Customer).where(Customer.status == "inactive").order_by(Customer.name)
        return list(self.db.execute(stmt).scalars().all())

    def update(
        self,
        customer: Customer,
        area: Optional[str] = None,
        mobile: Optional[str] = None,
        subscription: Optional[str] = None,
        custom_rate: Optional[float] = None,
        end_date: Optional[date] = None,
    ) -> Customer:
        """Update customer details."""
        if area is not None:
            customer.area = area
        if mobile is not None:
            customer.mobile = mobile
        if subscription is not None:
            customer.subscription = subscription
        if custom_rate is not None:
            customer.custom_rate = custom_rate
        if end_date is not None:
            customer.end_date = end_date
        self.db.flush()
        return customer

    def deactivate(self, customer: Customer) -> Customer:
        """Deactivate customer (soft delete)."""
        customer.status = "inactive"
        self.db.flush()
        return customer

    def reactivate(self, customer: Customer) -> Customer:
        """Reactivate customer."""
        customer.status = "active"
        self.db.flush()
        return customer

    def delete(self, customer: Customer) -> None:
        """Delete customer permanently."""
        self.db.delete(customer)
        self.db.flush()
