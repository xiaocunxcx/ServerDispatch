from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from internal.db.models.common import BaseModel


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    actor_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    action_type: Mapped[str] = mapped_column(String(200), nullable=False)
    target_type: Mapped[str | None] = mapped_column(String(200), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    meta: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    actor = relationship("User", back_populates="audit_logs")
