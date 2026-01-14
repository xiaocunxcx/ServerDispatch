from __future__ import annotations

from datetime import datetime

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from internal.db.models.reservation import Reservation, ReservationMode, ReservationStatus

ACTIVE_STATUSES = {ReservationStatus.scheduled, ReservationStatus.active}


def time_overlaps(start_time: datetime, end_time: datetime, other_start: datetime, other_end: datetime) -> bool:
    return start_time < other_end and end_time > other_start


def build_conflict_query(
    db: Session,
    server_id: str,
    card_id: str | None,
    mode: ReservationMode,
    start_time: datetime,
    end_time: datetime,
):
    overlap_window = and_(Reservation.start_time < end_time, Reservation.end_time > start_time)
    base = db.query(Reservation).filter(
        overlap_window,
        Reservation.status.in_(ACTIVE_STATUSES),
        Reservation.server_id == server_id,
    )

    if mode == ReservationMode.full_machine:
        return base

    return base.filter(
        or_(
            Reservation.mode == ReservationMode.full_machine,
            Reservation.card_id == card_id,
        )
    )


def has_conflict(
    db: Session,
    server_id: str,
    card_id: str | None,
    mode: ReservationMode,
    start_time: datetime,
    end_time: datetime,
) -> bool:
    return build_conflict_query(db, server_id, card_id, mode, start_time, end_time).first() is not None
