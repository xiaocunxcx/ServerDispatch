from __future__ import annotations

import enum

from sqlalchemy import Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from internal.db.models.common import BaseModel


class CardStatus(str, enum.Enum):
    free = "free"
    occupied = "occupied"
    self = "self"
    offline = "offline"


class NPUCard(BaseModel):
    __tablename__ = "npu_cards"
    __table_args__ = (UniqueConstraint("server_id", "index", name="uq_cards_server_index"),)

    server_id: Mapped[str] = mapped_column(ForeignKey("servers.id"), nullable=False)
    index: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[CardStatus] = mapped_column(Enum(CardStatus), nullable=False)
    current_reservation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    server = relationship("Server", back_populates="cards")
    reservations = relationship("Reservation", back_populates="card")
    metrics = relationship("MetricSnapshot", back_populates="card")
    alerts = relationship("Alert", back_populates="card")
