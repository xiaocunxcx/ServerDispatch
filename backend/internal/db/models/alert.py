from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from internal.db.models.common import BaseModel


class AlertType(str, enum.Enum):
    no_reservation_high_load = "no_reservation_high_load"
    reservation_zero_load = "reservation_zero_load"


class AlertStatus(str, enum.Enum):
    open = "open"
    resolved = "resolved"


class Alert(BaseModel):
    __tablename__ = "alerts"

    server_id: Mapped[str] = mapped_column(ForeignKey("servers.id"), nullable=False)
    card_id: Mapped[str | None] = mapped_column(ForeignKey("npu_cards.id"), nullable=True)
    type: Mapped[AlertType] = mapped_column(Enum(AlertType), nullable=False)
    status: Mapped[AlertStatus] = mapped_column(Enum(AlertStatus), nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    server = relationship("Server", back_populates="alerts")
    card = relationship("NPUCard", back_populates="alerts")
