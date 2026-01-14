from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from internal.db.models.alert import Alert, AlertStatus, AlertType
from internal.db.models.reservation import Reservation, ReservationMode, ReservationStatus

HIGH_UTIL_THRESHOLD = 0.7
LOW_UTIL_THRESHOLD = 0.05


class AlertService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def evaluate_snapshot(self, snapshot, timestamp: datetime | None = None) -> list[Alert]:
        if not snapshot.card_id:
            return []

        observed_at = timestamp or snapshot.timestamp
        has_reservation = self._has_active_reservation(snapshot.server_id, snapshot.card_id, observed_at)
        ai_util = snapshot.ai_core_util or 0.0

        alerts: list[Alert] = []
        alerts.extend(
            self._upsert_alert(
                snapshot,
                AlertType.no_reservation_high_load,
                condition=(not has_reservation and ai_util >= HIGH_UTIL_THRESHOLD),
                observed_at=observed_at,
            )
        )
        alerts.extend(
            self._upsert_alert(
                snapshot,
                AlertType.reservation_zero_load,
                condition=(has_reservation and ai_util <= LOW_UTIL_THRESHOLD),
                observed_at=observed_at,
            )
        )
        return alerts

    def _has_active_reservation(self, server_id: str, card_id: str, timestamp: datetime) -> bool:
        active_statuses = [ReservationStatus.scheduled, ReservationStatus.active]
        reservations = (
            self.db.query(Reservation)
            .filter(
                Reservation.server_id == server_id,
                Reservation.status.in_(active_statuses),
                Reservation.start_time <= timestamp,
                Reservation.end_time > timestamp,
            )
            .all()
        )
        for reservation in reservations:
            if reservation.mode == ReservationMode.full_machine:
                return True
            if reservation.card_id == card_id:
                return True
        return False

    def _upsert_alert(
        self,
        snapshot,
        alert_type: AlertType,
        condition: bool,
        observed_at: datetime,
    ) -> list[Alert]:
        existing = (
            self.db.query(Alert)
            .filter(
                Alert.server_id == snapshot.server_id,
                Alert.card_id == snapshot.card_id,
                Alert.type == alert_type,
                Alert.status == AlertStatus.open,
            )
            .one_or_none()
        )

        if condition and not existing:
            alert = Alert(
                server_id=snapshot.server_id,
                card_id=snapshot.card_id,
                type=alert_type,
                status=AlertStatus.open,
                detected_at=observed_at,
                resolved_at=None,
            )
            self.db.add(alert)
            return [alert]

        if not condition and existing:
            existing.status = AlertStatus.resolved
            existing.resolved_at = observed_at
            self.db.add(existing)
            return [existing]

        return []
