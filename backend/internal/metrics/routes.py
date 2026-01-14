from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from internal.auth.deps import get_current_user
from internal.db.models.alert import AlertStatus
from internal.db.models.metric_snapshot import MetricSnapshot
from internal.db.models.user import User
from internal.db.session import get_db
from internal.metrics.alerts import AlertService
from internal.metrics.service import MetricSnapshotInput, MetricsService
from internal.metrics.summary import ServerSummary, build_dashboard_summary

router = APIRouter(tags=["metrics"])


class MetricSnapshotPayload(BaseModel):
    card_index: int
    timestamp: datetime
    ai_core_util: float | None = None
    hbm_used: float | None = None
    hbm_total: float | None = None
    temperature: float | None = None


class MetricsIngestRequest(BaseModel):
    server_id: str
    snapshots: list[MetricSnapshotPayload]


class MetricsIngestResponse(BaseModel):
    ingested_count: int


class MetricSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    server_id: str
    card_id: str | None
    timestamp: datetime
    ai_core_util: float | None
    hbm_used: float | None
    hbm_total: float | None
    temperature: float | None


class MetricsListResponse(BaseModel):
    metrics: list[MetricSnapshotResponse]


class DashboardSummaryResponse(BaseModel):
    servers: list[ServerSummary]


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    server_id: str
    card_id: str | None
    type: str
    status: str
    detected_at: datetime
    resolved_at: datetime | None


class AlertListResponse(BaseModel):
    alerts: list[AlertResponse]


@router.post("/metrics/ingest", response_model=MetricsIngestResponse)
def ingest_metrics(payload: MetricsIngestRequest, db: Session = Depends(get_db)) -> MetricsIngestResponse:
    service = MetricsService(db)
    inputs = [
        MetricSnapshotInput(
            card_index=snapshot.card_index,
            timestamp=snapshot.timestamp,
            ai_core_util=snapshot.ai_core_util,
            hbm_used=snapshot.hbm_used,
            hbm_total=snapshot.hbm_total,
            temperature=snapshot.temperature,
        )
        for snapshot in payload.snapshots
    ]
    persisted = service.persist_snapshots(payload.server_id, inputs)

    alert_service = AlertService(db)
    changed = False
    for snapshot in persisted:
        if alert_service.evaluate_snapshot(snapshot):
            changed = True

    if changed:
        db.commit()

    return MetricsIngestResponse(ingested_count=len(persisted))


@router.get("/metrics/servers/{server_id}", response_model=MetricsListResponse)
def get_server_metrics(
    server_id: str,
    window_seconds: int = Query(default=1800, ge=1),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MetricsListResponse:
    _ = user
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=window_seconds)
    metrics = (
        db.query(MetricSnapshot)
        .filter(MetricSnapshot.server_id == server_id, MetricSnapshot.timestamp >= cutoff)
        .order_by(MetricSnapshot.timestamp.desc())
        .all()
    )
    return MetricsListResponse(
        metrics=[MetricSnapshotResponse.model_validate(item) for item in metrics]
    )


@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DashboardSummaryResponse:
    summaries = build_dashboard_summary(db, user)
    return DashboardSummaryResponse(servers=summaries)


@router.get("/alerts", response_model=AlertListResponse)
def list_alerts(
    status: AlertStatus | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AlertListResponse:
    _ = user
    from internal.db.models.alert import Alert

    query = db.query(Alert)
    if status is None:
        query = query.filter(Alert.status == AlertStatus.open)
    else:
        query = query.filter(Alert.status == status)

    alerts = query.order_by(Alert.detected_at.desc()).all()
    return AlertListResponse(
        alerts=[AlertResponse.model_validate(item) for item in alerts]
    )
