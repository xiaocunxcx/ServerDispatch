from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from internal.api.errors import ApiError
from internal.db.models.metric_snapshot import MetricSnapshot
from internal.db.models.npu_card import NPUCard
from internal.db.models.server import Server


@dataclass(frozen=True)
class MetricSnapshotInput:
    card_index: int | None
    timestamp: datetime
    ai_core_util: float | None
    hbm_used: float | None
    hbm_total: float | None
    temperature: float | None


class MetricsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def persist_snapshots(
        self, server_id: str, snapshots: list[MetricSnapshotInput]
    ) -> list[MetricSnapshot]:
        if not snapshots:
            raise ApiError(code="no_snapshots", message="No snapshots provided", status_code=400)

        server = self.db.query(Server).filter(Server.id == server_id).one_or_none()
        if not server:
            raise ApiError(code="server_not_found", message="Server not found", status_code=404)

        cards = (
            self.db.query(NPUCard).filter(NPUCard.server_id == server_id).all()
        )
        card_map = {card.index: card for card in cards}

        metric_rows: list[MetricSnapshot] = []
        for snapshot in snapshots:
            if snapshot.card_index is None:
                raise ApiError(code="missing_card", message="Card index required", status_code=400)
            card = card_map.get(snapshot.card_index)
            if not card:
                raise ApiError(
                    code="card_not_found",
                    message=f"Card index {snapshot.card_index} not found",
                    status_code=404,
                )
            if snapshot.timestamp.tzinfo is None:
                raise ApiError(code="invalid_time", message="Timestamp must be timezone-aware")

            metric_rows.append(
                MetricSnapshot(
                    server_id=server_id,
                    card_id=card.id,
                    timestamp=snapshot.timestamp,
                    ai_core_util=snapshot.ai_core_util,
                    hbm_used=snapshot.hbm_used,
                    hbm_total=snapshot.hbm_total,
                    temperature=snapshot.temperature,
                )
            )

        self.db.add_all(metric_rows)
        self.db.commit()
        for row in metric_rows:
            self.db.refresh(row)
        return metric_rows
