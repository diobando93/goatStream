"""stream: make event_id nullable, add name column for channels

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-28

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("streams", "event_id", existing_type=sa.UUID(), nullable=True)
    op.add_column("streams", sa.Column("name", sa.String(256), nullable=True))


def downgrade() -> None:
    op.drop_column("streams", "name")
    # Will fail if any channel streams (event_id=NULL) still exist
    op.alter_column("streams", "event_id", existing_type=sa.UUID(), nullable=False)
