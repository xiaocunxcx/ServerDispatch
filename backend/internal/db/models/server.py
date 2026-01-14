from __future__ import annotations

import enum

from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from internal.db.models.common import BaseModel, TimestampMixin


class ServerStatus(str, enum.Enum):
    online = "online"
    offline = "offline"
    unknown = "unknown"


class Server(BaseModel, TimestampMixin):
    __tablename__ = "servers"

    hostname: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ip: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    access_account: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[ServerStatus] = mapped_column(Enum(ServerStatus), nullable=False)
    model: Mapped[str | None] = mapped_column(String(50), nullable=True)
    card_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chip_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hbm_gb: Mapped[int | None] = mapped_column(Integer, nullable=True)

    cards = relationship("NPUCard", back_populates="server", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="server")
    metrics = relationship("MetricSnapshot", back_populates="server")
    alerts = relationship("Alert", back_populates="server")
