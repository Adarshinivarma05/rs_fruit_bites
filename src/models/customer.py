"""Customer model."""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Customer(Base):
    """Customer database model."""

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    area: Mapped[Optional[str]] = mapped_column(String(100))
    mobile: Mapped[Optional[str]] = mapped_column(String(20))
    subscription: Mapped[str] = mapped_column(String(20), default="Basic")
    custom_rate: Mapped[float] = mapped_column(Float, default=0.0)
    start_date: Mapped[date] = mapped_column(Date, default=func.current_date())
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Customer(name={self.name}, subscription={self.subscription}, status={self.status})>"
