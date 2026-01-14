from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from internal.api.errors import ApiError
from internal.auth.permissions import require_admin
from internal.db.models.reservation import Reservation, ReservationStatus
from internal.db.models.user import User
from internal.db.session import get_db

router = APIRouter(prefix="/reservations", tags=["reservations"])


class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    server_id: str
    card_id: str | None
    status: ReservationStatus
    start_time: datetime
    end_time: datetime


@router.post("/{reservation_id}/force-release", response_model=ReservationResponse)
def force_release(
    reservation_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> ReservationResponse:
    _ = admin
    reservation = (
        db.query(Reservation).filter(Reservation.id == reservation_id).one_or_none()
    )
    if not reservation:
        raise ApiError(code="reservation_not_found", message="Reservation not found", status_code=404)

    if reservation.status in {
        ReservationStatus.canceled,
        ReservationStatus.completed,
        ReservationStatus.forced_release,
    }:
        raise ApiError(
            code="invalid_status",
            message="Reservation cannot be force released",
            status_code=409,
        )

    now = datetime.now(timezone.utc)
    reservation.status = ReservationStatus.forced_release
    end_time = reservation.end_time
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)
    if end_time > now:
        reservation.end_time = now
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return ReservationResponse.model_validate(reservation)
