from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from internal.db.models.common import BaseModel, TimestampMixin


class Team(BaseModel, TimestampMixin):
    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)

    users = relationship("User", back_populates="team")
