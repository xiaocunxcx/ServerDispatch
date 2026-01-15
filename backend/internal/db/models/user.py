from __future__ import annotations

import enum

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from internal.db.models.common import BaseModel, TimestampMixin


class UserStatus(str, enum.Enum):
    active = "active"
    disabled = "disabled"


class User(BaseModel, TimestampMixin):
    __tablename__ = "users"

    ldap_id: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    ssh_login: Mapped[str] = mapped_column(String(200), nullable=False)
    ssh_public_key: Mapped[str | None] = mapped_column(String, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    team_id: Mapped[str | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), nullable=False)

    team = relationship("Team", back_populates="users")
    reservations = relationship("Reservation", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="actor")
