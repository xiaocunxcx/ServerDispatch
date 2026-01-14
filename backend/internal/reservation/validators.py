from __future__ import annotations

from datetime import datetime

from internal.api.errors import ApiError
from internal.db.models.reservation import ReservationMode


def validate_time_window(start_time: datetime, end_time: datetime) -> None:
    if start_time.tzinfo is None or end_time.tzinfo is None:
        raise ApiError(code="invalid_time", message="Timezone-aware datetimes required")
    if start_time >= end_time:
        raise ApiError(code="invalid_time", message="Start time must be before end time")


def validate_mode_and_card(mode: ReservationMode, card_id: str | None) -> None:
    if mode == ReservationMode.carpool and not card_id:
        raise ApiError(code="missing_card", message="Card ID required for carpool mode")
    if mode == ReservationMode.full_machine and card_id:
        raise ApiError(code="invalid_card", message="Card ID not allowed for full machine mode")
