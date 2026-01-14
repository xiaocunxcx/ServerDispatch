from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from internal.db.models.audit_log import AuditLog


class AuditService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def log_action(
        self,
        actor_user_id: str,
        action_type: str,
        target_type: str | None = None,
        target_id: str | None = None,
        metadata: dict | None = None,
        timestamp: datetime | None = None,
    ) -> AuditLog:
        log = AuditLog(
            actor_user_id=actor_user_id,
            action_type=action_type,
            target_type=target_type,
            target_id=target_id,
            timestamp=timestamp or datetime.now(timezone.utc),
            meta=metadata,
        )
        self.db.add(log)
        return log

    def list_logs(self, start: datetime | None, end: datetime | None) -> list[AuditLog]:
        query = self.db.query(AuditLog)
        if start:
            query = query.filter(AuditLog.timestamp >= start)
        if end:
            query = query.filter(AuditLog.timestamp <= end)
        return query.order_by(AuditLog.timestamp.desc()).all()
