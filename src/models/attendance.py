"""Attendance model."""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Attendance(Base):
    """Attendance database model."""

    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("date", "name", name="uq_attendance_date_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    subscription: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    extra_bowls: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    def __repr__(self) -> str:
        return f"<Attendance(date={self.date}, name={self.name}, status={self.status})>"
