from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from internal.db.models.reservation import Reservation, ReservationStatus
from internal.db.session import SessionLocal


def activate_due_reservations(db: Session, now: datetime) -> int:
    reservations = (
        db.query(Reservation)
        .filter(
            Reservation.status == ReservationStatus.scheduled,
            Reservation.start_time <= now,
            Reservation.end_time > now,
        )
        .all()
    )
    for reservation in reservations:
        reservation.status = ReservationStatus.active
    if reservations:
        db.commit()
    return len(reservations)


def expire_due_reservations(db: Session, now: datetime) -> int:
    reservations = (
        db.query(Reservation)
        .filter(
            Reservation.status == ReservationStatus.active,
            Reservation.end_time <= now,
        )
        .all()
    )
    for reservation in reservations:
        reservation.status = ReservationStatus.completed
    if reservations:
        db.commit()
    return len(reservations)


async def run_activation_job() -> None:
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        activate_due_reservations(db, now)


async def run_expiration_job() -> None:
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        expire_due_reservations(db, now)
