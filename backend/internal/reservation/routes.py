from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from internal.auth.deps import get_current_user
from internal.db.models.reservation import ReservationMode, ReservationStatus
from internal.db.models.user import User
from internal.db.session import get_db
from internal.reservation.service import ReservationService

router = APIRouter(prefix="/reservations", tags=["reservations"])


class ReservationCreateRequest(BaseModel):
    server_id: str
    mode: ReservationMode
    card_index: int | None = None
    start_time: datetime
    end_time: datetime


class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    server_id: str
    card_id: str | None
    mode: ReservationMode
    start_time: datetime
    end_time: datetime
    status: ReservationStatus
    environment_hint: str | None


class ReservationListResponse(BaseModel):
    reservations: list[ReservationResponse]


@router.get("", response_model=ReservationListResponse)
def list_reservations(
    user_id: str | None = Query(default=None),
    server_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    start_from: datetime | None = Query(default=None, alias="from"),
    end_to: datetime | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ReservationListResponse:
    service = ReservationService(db)
    reservations = service.list_reservations(user, user_id, server_id, status, start_from, end_to)
    return ReservationListResponse(
        reservations=[ReservationResponse.model_validate(r) for r in reservations]
    )


@router.post("", response_model=ReservationResponse, status_code=201)
def create_reservation(
    payload: ReservationCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ReservationResponse:
    service = ReservationService(db)
    reservation = service.create_reservation(
        user=user,
        server_id=payload.server_id,
        mode=payload.mode,
        start_time=payload.start_time,
        end_time=payload.end_time,
        card_index=payload.card_index,
    )
    return ReservationResponse.model_validate(reservation)


@router.post("/{reservation_id}/cancel", response_model=ReservationResponse)
def cancel_reservation(
    reservation_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ReservationResponse:
    service = ReservationService(db)
    reservation = service.cancel_reservation(user, reservation_id)
    return ReservationResponse.model_validate(reservation)
