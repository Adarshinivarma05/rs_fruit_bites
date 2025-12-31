"""Payment service for business logic."""
from datetime import date
from typing import List

import pandas as pd
from sqlalchemy.orm import Session

from src.repositories.payment_repository import PaymentRepository
from src.repositories.audit_repository import AuditRepository


class PaymentService:
    """Service for payment business logic."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.audit_repo = AuditRepository(db)

    def record_payment(
        self,
        payment_date: date,
        name: str,
        amount: float,
        method: str = "Cash",
        remarks: str = "",
        month: str = "",
    ) -> dict:
        """Record a new payment."""
        if amount <= 0:
            raise ValueError("Payment amount must be greater than 0")

        payment = self.payment_repo.create(
            payment_date=payment_date,
            name=name,
            amount=amount,
            method=method,
            remarks=remarks,
            month=month,
        )

        self.audit_repo.log_action("ADD_PAYMENT", f"Payment recorded: {name} - ₹{amount}")
        self.db.commit()

        return {
            "id": payment.id,
            "date": payment.date.isoformat(),
            "name": payment.name,
            "amount": payment.amount,
            "method": payment.method,
            "remarks": payment.remarks,
        }

    def get_all_payments(self) -> pd.DataFrame:
        """Get all payment records."""
        payments = self.payment_repo.get_all()
        if not payments:
            return pd.DataFrame()

        data = [
            {
                "id": p.id,
                "date": p.date.isoformat(),
                "name": p.name,
                "amount": p.amount,
                "method": p.method,
                "remarks": p.remarks or "",
                "month": p.month or "",
            }
            for p in payments
        ]
        return pd.DataFrame(data)

    def get_payments_by_range(self, start_date: date, end_date: date) -> pd.DataFrame:
        """Get payments within a date range."""
        payments = self.payment_repo.get_by_date_range(start_date, end_date)
        if not payments:
            return pd.DataFrame()

        data = [
            {
                "id": p.id,
                "date": p.date.isoformat(),
                "name": p.name,
                "amount": p.amount,
                "method": p.method,
                "remarks": p.remarks or "",
            }
            for p in payments
        ]
        return pd.DataFrame(data)

    def delete_payment(self, payment_id: int) -> bool:
        """Delete a payment by its ID and audit the action."""
        deleted = self.payment_repo.delete_by_id(payment_id)
        if deleted:
            self.audit_repo.log_action("DELETE_PAYMENT", f"Payment deleted: id={payment_id}")
            self.db.commit()
        return deleted

    def get_customer_payments(self, name: str) -> pd.DataFrame:
        """Get all payments for a customer."""
        payments = self.payment_repo.get_by_customer(name)
        if not payments:
            return pd.DataFrame()

        data = [
            {
                "date": p.date.isoformat(),
                "amount": p.amount,
                "method": p.method,
                "remarks": p.remarks or "",
            }
            for p in payments
        ]
        return pd.DataFrame(data)
