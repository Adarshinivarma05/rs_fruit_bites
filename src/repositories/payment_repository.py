"""Payment repository for database operations."""
from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.payment import Payment


class PaymentRepository:
    """Repository for payment database operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        payment_date: date,
        name: str,
        amount: float,
        method: str = "Cash",
        remarks: str = "",
        month: str = "",
    ) -> Payment:
        """Create a new payment record."""
        payment = Payment(
            date=payment_date,
            name=name,
            amount=amount,
            method=method,
            remarks=remarks,
            month=month,
        )
        self.db.add(payment)
        self.db.flush()
        return payment

    def get_by_id(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID."""
        return self.db.get(Payment, payment_id)

    def get_all(self) -> List[Payment]:
        """Get all payment records."""
        stmt = select(Payment).order_by(Payment.date.desc(), Payment.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def get_by_date_range(self, start_date: date, end_date: date) -> List[Payment]:
        """Get payments within a date range."""
        stmt = (
            select(Payment)
            .where(Payment.date >= start_date, Payment.date <= end_date)
            .order_by(Payment.date.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_customer(self, name: str) -> List[Payment]:
        """Get all payments for a customer."""
        stmt = select(Payment).where(Payment.name == name).order_by(Payment.date.desc())
        return list(self.db.execute(stmt).scalars().all())

    def delete_by_id(self, payment_id: int) -> bool:
        """Delete a payment by ID. Returns True if deleted, False if not found."""
        obj = self.get_by_id(payment_id)
        if obj is None:
            return False
        self.db.delete(obj)
        return True
