from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from internal.config.settings import get_settings
from internal.db.models.metric_snapshot import MetricSnapshot
from internal.db.session import SessionLocal


def purge_old_snapshots(db: Session, cutoff: datetime) -> int:
    deleted = db.query(MetricSnapshot).filter(MetricSnapshot.timestamp < cutoff).delete()
    db.commit()
    return deleted


async def run_retention_job() -> None:
    settings = get_settings()
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.metrics_retention_days)
    with SessionLocal() as db:
        purge_old_snapshots(db, cutoff)
