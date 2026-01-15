"""add password hash to users

Revision ID: 0002_add_password_hash
Revises: 0001_initial
Create Date: 2026-01-15 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_add_password_hash"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "password_hash")
