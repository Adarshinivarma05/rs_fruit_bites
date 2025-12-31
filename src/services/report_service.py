"""Report service for analytics and reporting."""
from typing import List

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.attendance import Attendance
from src.models.customer import Customer
from src.models.payment import Payment
from src.repositories.audit_repository import AuditRepository


class ReportService:
    """Service for reports and analytics."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.audit_repo = AuditRepository(db)

    def get_pending_bills(self) -> pd.DataFrame:
        """Calculate pending bills for all active customers."""
        stmt = (
            select(
                Customer.name,
                Customer.subscription,
                Customer.custom_rate,
                func.coalesce(func.sum(Payment.amount), 0).label("total_paid"),
                func.count(Attendance.id).label("days_present"),
            )
            .outerjoin(Payment, Customer.name == Payment.name)
            .outerjoin(
                Attendance,
                (Customer.name == Attendance.name)
                & (Attendance.status.in_(["Present", "Extra"])),
            )
            .where(Customer.status == "active")
            .group_by(Customer.name, Customer.subscription, Customer.custom_rate)
            .order_by(Customer.name)
        )

        result = self.db.execute(stmt).all()

        if not result:
            return pd.DataFrame()

        data = []
        for row in result:
            custom_rate = row.custom_rate or 0
            days_present = row.days_present or 0
            total_paid = float(row.total_paid or 0)

            estimated_bill = custom_rate if custom_rate > 0 else days_present * 30
            pending = estimated_bill - total_paid

            data.append(
                {
                    "name": row.name,
                    "subscription": row.subscription,
                    "days_present": days_present,
                    "total_paid": total_paid,
                    "estimated_bill": estimated_bill,
                    "pending": pending,
                }
            )

        return pd.DataFrame(data)

    def get_dashboard_metrics(self) -> dict:
        """Get key metrics for dashboard."""
        from datetime import date

        total_customers = self.db.query(func.count(Customer.id)).filter(
            Customer.status == "active"
        ).scalar()

        today = date.today()
        today_attendance = (
            self.db.query(Attendance)
            .filter(
                Attendance.date == today,
                Attendance.status.in_(["Present", "Extra"]),
            )
            .all()
        )

        present_today = len(today_attendance)
        extra_bowls_today = sum(a.extra_bowls for a in today_attendance)

        return {
            "total_customers": total_customers or 0,
            "present_today": present_today,
            "extra_bowls_today": extra_bowls_today,
        }

    def get_deleted_members(self) -> pd.DataFrame:
        """Get audit log of deleted members."""
        deleted = self.audit_repo.get_deleted_members()
        if not deleted:
            return pd.DataFrame()

        data = [
            {
                "name": d.name,
                "area": d.area or "",
                "mobile": d.mobile or "",
                "subscription": d.subscription,
                "custom_rate": d.custom_rate,
                "start_date": d.start_date.isoformat() if d.start_date else "",
                "end_date": d.end_date.isoformat() if d.end_date else "",
                "deleted_at": d.deleted_at.isoformat(),
                "reason": d.reason or "",
            }
            for d in deleted
        ]
        return pd.DataFrame(data)
