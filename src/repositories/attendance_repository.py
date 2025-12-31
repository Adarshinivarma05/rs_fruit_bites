"""Attendance repository for database operations."""
from datetime import date
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.attendance import Attendance


class AttendanceRepository:
    """Repository for attendance database operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_or_update(
        self,
        attendance_date: date,
        name: str,
        subscription: str,
        status: str,
        extra_bowls: int = 0,
    ) -> Attendance:
        """Create or update attendance record."""
        stmt = select(Attendance).where(
            Attendance.date == attendance_date, Attendance.name == name
        )
        attendance = self.db.execute(stmt).scalar_one_or_none()

        if attendance:
            attendance.subscription = subscription
            attendance.status = status
            attendance.extra_bowls = extra_bowls
        else:
            attendance = Attendance(
                date=attendance_date,
                name=name,
                subscription=subscription,
                status=status,
                extra_bowls=extra_bowls,
            )
            self.db.add(attendance)

        self.db.flush()
        return attendance

    def get_by_date(self, attendance_date: date) -> List[Attendance]:
        """Get all attendance records for a specific date."""
        stmt = (
            select(Attendance)
            .where(Attendance.date == attendance_date)
            .order_by(Attendance.name)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_date_range(self, start_date: date, end_date: date) -> List[Attendance]:
        """Get attendance records within a date range."""
        stmt = (
            select(Attendance)
            .where(Attendance.date >= start_date, Attendance.date <= end_date)
            .order_by(Attendance.date.desc(), Attendance.name)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_customer(self, name: str) -> List[Attendance]:
        """Get all attendance records for a customer."""
        stmt = select(Attendance).where(Attendance.name == name).order_by(Attendance.date.desc())
        return list(self.db.execute(stmt).scalars().all())
