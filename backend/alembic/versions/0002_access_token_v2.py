"""access_token: add token, status, created_at; drop active

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-08

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "access_tokens",
        sa.Column("token", sa.UUID(), nullable=True),
    )
    op.add_column(
        "access_tokens",
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
    )
    op.add_column(
        "access_tokens",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    # Backfill token for any pre-existing rows
    op.execute("UPDATE access_tokens SET token = gen_random_uuid() WHERE token IS NULL")
    op.alter_column("access_tokens", "token", nullable=False)
    op.create_unique_constraint("uq_access_tokens_token", "access_tokens", ["token"])
    op.drop_column("access_tokens", "active")


def downgrade() -> None:
    op.add_column(
        "access_tokens",
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.drop_constraint("uq_access_tokens_token", "access_tokens", type_="unique")
    op.drop_column("access_tokens", "created_at")
    op.drop_column("access_tokens", "status")
    op.drop_column("access_tokens", "token")
