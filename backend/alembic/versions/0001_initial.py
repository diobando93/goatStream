"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-03

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "access_tokens",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("type", sa.String(16), nullable=False, server_default="event"),
        sa.Column("status", sa.String(16), nullable=False, server_default="SCHEDULED"),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sport", sa.String(64), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "streams",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("event_id", sa.UUID(), nullable=False),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("type", sa.String(8), nullable=False),
        sa.Column("health", sa.String(8), nullable=False, server_default="unknown"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("streams")
    op.drop_table("events")
    op.drop_table("access_tokens")
