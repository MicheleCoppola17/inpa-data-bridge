"""add settore column

Revision ID: 20260321_0006
Revises: f3c6f6749e81
Create Date: 2026-03-21 18:48:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260321_0006"
down_revision: Union[str, None] = "f3c6f6749e81"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the column as nullable first so the ALTER doesn't fail on existing rows
    op.add_column("exams", sa.Column("settore", sa.Text(), nullable=True))
    # Back-fill existing rows with the safe default
    op.execute("UPDATE exams SET settore = 'Altro'")
    # Tighten to NOT NULL now that every row has a value
    op.alter_column("exams", "settore", nullable=False)


def downgrade() -> None:
    op.drop_column("exams", "settore")
