from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload

from internal.auth.deps import get_current_user
from internal.db.models.npu_card import CardStatus, NPUCard
from internal.db.models.reservation import Reservation, ReservationMode, ReservationStatus
from internal.db.models.server import Server, ServerStatus
from internal.db.models.user import User
from internal.db.session import get_db

router = APIRouter(prefix="/servers", tags=["inventory"])


class CardResponse(BaseModel):
    id: str
    index: int
    status: str
    current_reservation_id: str | None


class ServerResponse(BaseModel):
    id: str
    hostname: str | None
    ip: str
    status: str
    model: str | None
    card_count: int | None
    chip_id: str | None
    hbm_gb: int | None
    cards: list[CardResponse]


class ServerListResponse(BaseModel):
    servers: list[ServerResponse]


@router.get("", response_model=ServerListResponse)
def list_servers(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ServerListResponse:
    servers = db.query(Server).options(selectinload(Server.cards)).all()
    if not servers:
        return ServerListResponse(servers=[])

    server_ids = [server.id for server in servers]
    now = datetime.now(timezone.utc)
    active_statuses = [ReservationStatus.scheduled, ReservationStatus.active]
    reservations = (
        db.query(Reservation)
        .filter(
            Reservation.server_id.in_(server_ids),
            Reservation.status.in_(active_statuses),
            Reservation.start_time <= now,
            Reservation.end_time > now,
        )
        .all()
    )

    full_machine_map: dict[str, Reservation] = {}
    card_reservation_map: dict[str, Reservation] = {}

    for reservation in reservations:
        if reservation.mode == ReservationMode.full_machine:
            full_machine_map.setdefault(reservation.server_id, reservation)
        elif reservation.card_id:
            card_reservation_map.setdefault(reservation.card_id, reservation)

    response_servers: list[ServerResponse] = []
    for server in servers:
        server_cards: list[CardResponse] = []
        full_machine_res = full_machine_map.get(server.id)
        for card in server.cards:
            status = CardStatus.free.value
            current_reservation_id = None

            if server.status == ServerStatus.offline or card.status == CardStatus.offline:
                status = CardStatus.offline.value
            elif full_machine_res:
                current_reservation_id = full_machine_res.id
                status = (
                    CardStatus.self.value
                    if full_machine_res.user_id == user.id
                    else CardStatus.occupied.value
                )
            else:
                card_res = card_reservation_map.get(card.id)
                if card_res:
                    current_reservation_id = card_res.id
                    status = (
                        CardStatus.self.value
                        if card_res.user_id == user.id
                        else CardStatus.occupied.value
                    )

            server_cards.append(
                CardResponse(
                    id=card.id,
                    index=card.index,
                    status=status,
                    current_reservation_id=current_reservation_id,
                )
            )

        response_servers.append(
            ServerResponse(
                id=server.id,
                hostname=server.hostname,
                ip=server.ip,
                status=server.status.value,
                model=server.model,
                card_count=server.card_count,
                chip_id=server.chip_id,
                hbm_gb=server.hbm_gb,
                cards=server_cards,
            )
        )

    return ServerListResponse(servers=response_servers)
