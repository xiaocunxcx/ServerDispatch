from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload

from internal.db.models.npu_card import CardStatus
from internal.db.models.reservation import Reservation, ReservationMode, ReservationStatus
from internal.db.models.server import Server, ServerStatus
from internal.db.models.user import User


class ServerSummaryCard(BaseModel):
    card_index: int
    status: str
    reservation_id: str | None


class ServerSummary(BaseModel):
    server_id: str
    server_name: str | None
    cards: list[ServerSummaryCard]


def build_dashboard_summary(db: Session, user: User) -> list[ServerSummary]:
    servers = db.query(Server).options(selectinload(Server.cards)).all()
    if not servers:
        return []

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

    summaries: list[ServerSummary] = []
    for server in servers:
        cards: list[ServerSummaryCard] = []
        full_machine_res = full_machine_map.get(server.id)
        for card in server.cards:
            status = CardStatus.free.value
            reservation_id = None
            if server.status == ServerStatus.offline or card.status == CardStatus.offline:
                status = CardStatus.offline.value
            elif full_machine_res:
                reservation_id = full_machine_res.id
                status = (
                    CardStatus.self.value
                    if full_machine_res.user_id == user.id
                    else CardStatus.occupied.value
                )
            else:
                card_res = card_reservation_map.get(card.id)
                if card_res:
                    reservation_id = card_res.id
                    status = (
                        CardStatus.self.value
                        if card_res.user_id == user.id
                        else CardStatus.occupied.value
                    )

            cards.append(
                ServerSummaryCard(
                    card_index=card.index,
                    status=status,
                    reservation_id=reservation_id,
                )
            )

        summaries.append(
            ServerSummary(
                server_id=server.id,
                server_name=server.hostname or server.ip,
                cards=cards,
            )
        )

    return summaries
