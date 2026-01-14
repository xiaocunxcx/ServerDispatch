from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload

from internal.api.errors import ApiError
from internal.db.models.npu_card import NPUCard
from internal.db.models.reservation import Reservation, ReservationMode, ReservationStatus
from internal.db.models.server import Server
from internal.db.models.user import User
from internal.db.session import get_db

router = APIRouter(prefix="/agent", tags=["agent"])


class AccessPolicyEntry(BaseModel):
    reservation_id: str
    user_id: str
    ssh_login: str
    ssh_public_key: str
    mode: ReservationMode
    card_id: str | None
    card_index: int | None
    start_time: datetime
    end_time: datetime
    environment_hint: str | None


class AccessPolicyResponse(BaseModel):
    server_id: str
    generated_at: datetime
    reservations: list[AccessPolicyEntry]


@router.get("/access-policy", response_model=AccessPolicyResponse)
def get_access_policy(
    server_id: str = Query(...),
    db: Session = Depends(get_db),
) -> AccessPolicyResponse:
    server = db.query(Server).filter(Server.id == server_id).one_or_none()
    if not server:
        raise ApiError(code="server_not_found", message="Server not found", status_code=404)

    now = datetime.now(timezone.utc)
    active_statuses = [ReservationStatus.scheduled, ReservationStatus.active]
    reservations = (
        db.query(Reservation)
        .options(selectinload(Reservation.user), selectinload(Reservation.card))
        .filter(
            Reservation.server_id == server_id,
            Reservation.status.in_(active_statuses),
            Reservation.start_time <= now,
            Reservation.end_time > now,
        )
        .all()
    )

    entries: list[AccessPolicyEntry] = []
    for reservation in reservations:
        user: User | None = reservation.user
        if not user or not user.ssh_public_key:
            continue
        card: NPUCard | None = reservation.card
        entries.append(
            AccessPolicyEntry(
                reservation_id=reservation.id,
                user_id=user.id,
                ssh_login=user.ssh_login,
                ssh_public_key=user.ssh_public_key,
                mode=reservation.mode,
                card_id=reservation.card_id,
                card_index=card.index if card else None,
                start_time=reservation.start_time,
                end_time=reservation.end_time,
                environment_hint=reservation.environment_hint,
            )
        )

    return AccessPolicyResponse(server_id=server_id, generated_at=now, reservations=entries)
