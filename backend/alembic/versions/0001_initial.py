"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-01-12 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    user_status = sa.Enum("active", "disabled", name="user_status")
    server_status = sa.Enum("online", "offline", "unknown", name="server_status")
    card_status = sa.Enum("free", "occupied", "self", "offline", name="card_status")
    reservation_mode = sa.Enum("full_machine", "carpool", name="reservation_mode")
    reservation_status = sa.Enum(
        "scheduled",
        "active",
        "completed",
        "canceled",
        "forced_release",
        name="reservation_status",
    )
    alert_type = sa.Enum(
        "no_reservation_high_load", "reservation_zero_load", name="alert_type"
    )
    alert_status = sa.Enum("open", "resolved", name="alert_status")

    op.create_table(
        "teams",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("ldap_id", sa.String(length=200), nullable=False, unique=True),
        sa.Column("ssh_login", sa.String(length=200), nullable=False),
        sa.Column("ssh_public_key", sa.String(), nullable=True),
        sa.Column("display_name", sa.String(length=200), nullable=True),
        sa.Column("team_id", sa.String(length=36), sa.ForeignKey("teams.id")),
        sa.Column("status", user_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "servers",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("hostname", sa.String(length=200), nullable=True),
        sa.Column("ip", sa.String(length=64), nullable=False, unique=True),
        sa.Column("access_account", sa.String(length=200), nullable=True),
        sa.Column("status", server_status, nullable=False),
        sa.Column("model", sa.String(length=50), nullable=True),
        sa.Column("card_count", sa.Integer(), nullable=True),
        sa.Column("chip_id", sa.String(length=100), nullable=True),
        sa.Column("hbm_gb", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "npu_cards",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("server_id", sa.String(length=36), sa.ForeignKey("servers.id"), nullable=False),
        sa.Column("index", sa.Integer(), nullable=False),
        sa.Column("status", card_status, nullable=False),
        sa.Column("current_reservation_id", sa.String(length=36), nullable=True),
        sa.UniqueConstraint("server_id", "index", name="uq_cards_server_index"),
    )

    op.create_table(
        "reservations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("server_id", sa.String(length=36), sa.ForeignKey("servers.id"), nullable=False),
        sa.Column("card_id", sa.String(length=36), sa.ForeignKey("npu_cards.id"), nullable=True),
        sa.Column("mode", reservation_mode, nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", reservation_status, nullable=False),
        sa.Column("environment_hint", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "metric_snapshots",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("server_id", sa.String(length=36), sa.ForeignKey("servers.id"), nullable=False),
        sa.Column("card_id", sa.String(length=36), sa.ForeignKey("npu_cards.id"), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ai_core_util", sa.Float(), nullable=True),
        sa.Column("hbm_used", sa.Float(), nullable=True),
        sa.Column("hbm_total", sa.Float(), nullable=True),
        sa.Column("temperature", sa.Float(), nullable=True),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("actor_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action_type", sa.String(length=200), nullable=False),
        sa.Column("target_type", sa.String(length=200), nullable=True),
        sa.Column("target_id", sa.String(length=36), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("server_id", sa.String(length=36), sa.ForeignKey("servers.id"), nullable=False),
        sa.Column("card_id", sa.String(length=36), sa.ForeignKey("npu_cards.id"), nullable=True),
        sa.Column("type", alert_type, nullable=False),
        sa.Column("status", alert_status, nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("alerts")
    op.drop_table("audit_logs")
    op.drop_table("metric_snapshots")
    op.drop_table("reservations")
    op.drop_table("npu_cards")
    op.drop_table("servers")
    op.drop_table("users")
    op.drop_table("teams")

    op.execute("DROP TYPE IF EXISTS alert_status")
    op.execute("DROP TYPE IF EXISTS alert_type")
    op.execute("DROP TYPE IF EXISTS reservation_status")
    op.execute("DROP TYPE IF EXISTS reservation_mode")
    op.execute("DROP TYPE IF EXISTS card_status")
    op.execute("DROP TYPE IF EXISTS server_status")
    op.execute("DROP TYPE IF EXISTS user_status")
