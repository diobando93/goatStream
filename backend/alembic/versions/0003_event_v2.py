"""event: rename name→title, add competition/teams/external_id/poster_url

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-08

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("events", "name", new_column_name="title")
    op.add_column("events", sa.Column("competition", sa.String(128), nullable=True))
    op.add_column("events", sa.Column("home_team", sa.String(128), nullable=True))
    op.add_column("events", sa.Column("away_team", sa.String(128), nullable=True))
    op.add_column("events", sa.Column("external_id", sa.String(64), nullable=True))
    op.add_column("events", sa.Column("poster_url", sa.String(2048), nullable=True))
    op.create_unique_constraint("uq_events_external_id", "events", ["external_id"])
    op.create_index("ix_events_external_id", "events", ["external_id"])


def downgrade() -> None:
    op.drop_index("ix_events_external_id", "events")
    op.drop_constraint("uq_events_external_id", "events", type_="unique")
    op.drop_column("events", "poster_url")
    op.drop_column("events", "external_id")
    op.drop_column("events", "away_team")
    op.drop_column("events", "home_team")
    op.drop_column("events", "competition")
    op.alter_column("events", "title", new_column_name="name")
