"""add short_description column

Revision ID: f3c6f6749e81
Revises: 20260306_0003
Create Date: 2026-03-18 23:24:29.470564
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3c6f6749e81'
down_revision: Union[str, None] = '20260306_0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('exams', sa.Column('short_description', sa.Text(), nullable=True))
    op.execute("UPDATE exams SET short_description = ''")
    op.alter_column('exams', 'short_description', nullable=False)


def downgrade() -> None:
    op.drop_column('exams', 'short_description')
