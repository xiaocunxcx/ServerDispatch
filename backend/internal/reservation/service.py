from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from internal.api.errors import ApiError
from internal.config.settings import get_settings
from internal.db.models.npu_card import CardStatus, NPUCard
from internal.db.models.reservation import Reservation, ReservationMode, ReservationStatus
from internal.db.models.server import Server, ServerStatus
from internal.db.models.user import User
from internal.reservation.conflict import has_conflict
from internal.reservation.validators import validate_mode_and_card, validate_time_window


class ReservationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_reservation(
        self,
        user: User,
        server_id: str,
        mode: ReservationMode,
        start_time: datetime,
        end_time: datetime,
        card_index: int | None,
    ) -> Reservation:
        validate_time_window(start_time, end_time)
        if not user.ssh_public_key:
            raise ApiError(code="missing_ssh_key", message="SSH public key required", status_code=400)

        server = self._get_server(server_id)
        if server.status == ServerStatus.offline:
            raise ApiError(code="server_offline", message="Server is offline", status_code=400)

        card_id = None
        if mode == ReservationMode.carpool:
            if card_index is None:
                raise ApiError(code="missing_card", message="Card index required", status_code=400)
            card = (
                self.db.query(NPUCard)
                .filter(NPUCard.server_id == server_id, NPUCard.index == card_index)
                .one_or_none()
            )
            if not card:
                raise ApiError(code="card_not_found", message="Card not found", status_code=404)
            if card.status == CardStatus.offline:
                raise ApiError(code="card_offline", message="Card is offline", status_code=400)
            card_id = card.id

        validate_mode_and_card(mode, card_id)

        if has_conflict(self.db, server_id, card_id, mode, start_time, end_time):
            raise ApiError(code="reservation_conflict", message="Reservation conflict", status_code=409)

        now = datetime.now(timezone.utc)
        if end_time <= now:
            raise ApiError(code="invalid_time", message="End time must be in the future", status_code=400)

        status = (
            ReservationStatus.active
            if start_time <= now < end_time
            else ReservationStatus.scheduled
        )
        environment_hint = (
            f"export ASCEND_VISIBLE_DEVICES={card_index}"
            if mode == ReservationMode.carpool and card_index is not None
            else None
        )

        reservation = Reservation(
            user_id=user.id,
            server_id=server_id,
            card_id=card_id,
            mode=mode,
            start_time=start_time,
            end_time=end_time,
            status=status,
            environment_hint=environment_hint,
        )
        self.db.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    def list_reservations(
        self,
        user: User,
        user_id: str | None,
        server_id: str | None,
        status: str | None,
        start_from: datetime | None,
        end_to: datetime | None,
    ) -> list[Reservation]:
        query = self.db.query(Reservation)

        if user_id:
            if user_id != user.id and not self._is_admin(user):
                raise ApiError(code="forbidden", message="Not allowed", status_code=403)
            query = query.filter(Reservation.user_id == user_id)
        else:
            query = query.filter(Reservation.user_id == user.id)

        if server_id:
            query = query.filter(Reservation.server_id == server_id)
        if status:
            try:
                status_enum = ReservationStatus(status)
            except ValueError as exc:
                raise ApiError(code="invalid_status", message="Invalid status", status_code=400) from exc
            query = query.filter(Reservation.status == status_enum)
        if start_from:
            query = query.filter(Reservation.end_time > start_from)
        if end_to:
            query = query.filter(Reservation.start_time < end_to)

        return query.order_by(Reservation.start_time.desc()).all()

    def cancel_reservation(self, user: User, reservation_id: str) -> Reservation:
        reservation = self._get_reservation(reservation_id)
        if reservation.user_id != user.id:
            raise ApiError(code="forbidden", message="Not allowed", status_code=403)
        if reservation.status != ReservationStatus.scheduled:
            raise ApiError(
                code="cannot_cancel",
                message="Only scheduled reservations can be canceled",
                status_code=409,
            )
        reservation.status = ReservationStatus.canceled
        self.db.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    def _get_server(self, server_id: str) -> Server:
        server = self.db.query(Server).filter(Server.id == server_id).one_or_none()
        if not server:
            raise ApiError(code="server_not_found", message="Server not found", status_code=404)
        return server

    def _get_reservation(self, reservation_id: str) -> Reservation:
        reservation = (
            self.db.query(Reservation).filter(Reservation.id == reservation_id).one_or_none()
        )
        if not reservation:
            raise ApiError(code="reservation_not_found", message="Reservation not found", status_code=404)
        return reservation

    def _is_admin(self, user: User) -> bool:
        settings = get_settings()
        return user.ldap_id in settings.admin_ldap_ids
