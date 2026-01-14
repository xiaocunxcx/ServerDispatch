from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from internal.db.models.common import BaseModel


class MetricSnapshot(BaseModel):
    __tablename__ = "metric_snapshots"

    server_id: Mapped[str] = mapped_column(ForeignKey("servers.id"), nullable=False)
    card_id: Mapped[str | None] = mapped_column(ForeignKey("npu_cards.id"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ai_core_util: Mapped[float | None] = mapped_column(Float, nullable=True)
    hbm_used: Mapped[float | None] = mapped_column(Float, nullable=True)
    hbm_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)

    server = relationship("Server", back_populates="metrics")
    card = relationship("NPUCard", back_populates="metrics")
