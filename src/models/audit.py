"""Audit and logging models."""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class AuditLog(Base):
    """Audit log for tracking system actions."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    details: Mapped[Optional[str]] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)

    def __repr__(self) -> str:
        return f"<AuditLog(action={self.action}, timestamp={self.timestamp})>"


class DeletedMember(Base):
    """Audit log for deleted customers."""

    __tablename__ = "deleted_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    area: Mapped[Optional[str]] = mapped_column(String(100))
    mobile: Mapped[Optional[str]] = mapped_column(String(20))
    subscription: Mapped[str] = mapped_column(String(20))
    custom_rate: Mapped[float] = mapped_column(Float)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)
    reason: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<DeletedMember(name={self.name}, deleted_at={self.deleted_at})>"
