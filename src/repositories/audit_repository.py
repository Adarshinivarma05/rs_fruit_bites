"""Audit repository for logging operations."""
from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.audit import AuditLog, DeletedMember
from src.models.customer import Customer


class AuditRepository:
    """Repository for audit logging operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def log_action(self, action: str, details: str = "") -> AuditLog:
        """Create an audit log entry."""
        log = AuditLog(action=action, details=details)
        self.db.add(log)
        self.db.flush()
        return log

    def get_logs(self, limit: int = 100) -> List[AuditLog]:
        """Get recent audit logs."""
        stmt = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def log_deleted_member(
        self,
        customer: Customer,
        reason: str = "",
    ) -> DeletedMember:
        """Log a deleted customer."""
        deleted = DeletedMember(
            name=customer.name,
            area=customer.area,
            mobile=customer.mobile,
            subscription=customer.subscription,
            custom_rate=customer.custom_rate,
            start_date=customer.start_date,
            end_date=customer.end_date,
            reason=reason,
        )
        self.db.add(deleted)
        self.db.flush()
        return deleted

    def get_deleted_members(self) -> List[DeletedMember]:
        """Get all deleted member records."""
        stmt = select(DeletedMember).order_by(DeletedMember.deleted_at.desc())
        return list(self.db.execute(stmt).scalars().all())
