from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from internal.db.models.common import BaseModel, TimestampMixin


class ReservationMode(str, enum.Enum):
    full_machine = "full_machine"
    carpool = "carpool"


class ReservationStatus(str, enum.Enum):
    scheduled = "scheduled"
    active = "active"
    completed = "completed"
    canceled = "canceled"
    forced_release = "forced_release"


class Reservation(BaseModel, TimestampMixin):
    __tablename__ = "reservations"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    server_id: Mapped[str] = mapped_column(ForeignKey("servers.id"), nullable=False)
    card_id: Mapped[str | None] = mapped_column(ForeignKey("npu_cards.id"), nullable=True)
    mode: Mapped[ReservationMode] = mapped_column(Enum(ReservationMode), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[ReservationStatus] = mapped_column(Enum(ReservationStatus), nullable=False)
    environment_hint: Mapped[str | None] = mapped_column(String(200), nullable=True)

    user = relationship("User", back_populates="reservations")
    server = relationship("Server", back_populates="reservations")
    card = relationship("NPUCard", back_populates="reservations")
