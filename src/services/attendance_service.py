"""Attendance service for business logic."""
from datetime import date
from typing import List

import pandas as pd
from sqlalchemy.orm import Session

from src.repositories.attendance_repository import AttendanceRepository
from src.services.customer_service import CustomerService


class AttendanceService:
    """Service for attendance business logic."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.attendance_repo = AttendanceRepository(db)
        self.customer_service = CustomerService(db)

    def mark_attendance(
        self,
        attendance_date: date,
        name: str,
        subscription: str,
        status: str,
        extra_bowls: int = 0,
    ) -> dict:
        """Mark attendance for a customer."""
        attendance = self.attendance_repo.create_or_update(
            attendance_date=attendance_date,
            name=name,
            subscription=subscription,
            status=status,
            extra_bowls=extra_bowls,
        )

        if status == "Absent":
            self.customer_service.extend_end_date(name, days=1)

        self.db.commit()

        return {
            "date": attendance.date.isoformat(),
            "name": attendance.name,
            "subscription": attendance.subscription,
            "status": attendance.status,
            "extra_bowls": attendance.extra_bowls,
        }

    def get_attendance_by_date(self, attendance_date: date) -> pd.DataFrame:
        """Get attendance records for a specific date."""
        records = self.attendance_repo.get_by_date(attendance_date)
        if not records:
            return pd.DataFrame()

        data = [
            {
                "date": r.date.isoformat(),
                "name": r.name,
                "subscription": r.subscription,
                "status": r.status,
                "extra_bowls": r.extra_bowls,
            }
            for r in records
        ]
        return pd.DataFrame(data)

    def get_attendance_by_range(self, start_date: date, end_date: date) -> pd.DataFrame:
        """Get attendance records within a date range."""
        records = self.attendance_repo.get_by_date_range(start_date, end_date)
        if not records:
            return pd.DataFrame()

        data = [
            {
                "date": r.date.isoformat(),
                "name": r.name,
                "subscription": r.subscription,
                "status": r.status,
                "extra_bowls": r.extra_bowls,
            }
            for r in records
        ]
        return pd.DataFrame(data)

    def get_customer_attendance(self, name: str) -> pd.DataFrame:
        """Get all attendance records for a customer."""
        records = self.attendance_repo.get_by_customer(name)
        if not records:
            return pd.DataFrame()

        data = [
            {
                "date": r.date.isoformat(),
                "status": r.status,
                "extra_bowls": r.extra_bowls,
            }
            for r in records
        ]
        return pd.DataFrame(data)
