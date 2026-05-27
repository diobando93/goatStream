"""stream: rename type→subtype, health→status; add last_checked_at

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-27

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("streams", "type", new_column_name="subtype")
    op.alter_column("streams", "health", new_column_name="status")
    op.add_column(
        "streams",
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("streams", "last_checked_at")
    op.alter_column("streams", "status", new_column_name="health")
    op.alter_column("streams", "subtype", new_column_name="type")
