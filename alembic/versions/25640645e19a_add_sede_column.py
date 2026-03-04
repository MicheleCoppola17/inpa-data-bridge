"""add sede and short_title columns

Revision ID: 25640645e19a
Revises: 20260304_0002
Create Date: 2026-03-04 11:54:16.916822
"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "25640645e19a"
down_revision: str | None = "20260304_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("exams", sa.Column("sede", sa.Text(), nullable=True))
    op.add_column("exams", sa.Column("short_title", sa.Text(), nullable=True))
    op.execute(
        """
        UPDATE exams
        SET short_title = TRIM(
            CONCAT(
                COALESCE(NULLIF(BTRIM(figura_ricercata), ''), 'Concorso'),
                CASE
                    WHEN num_posti IS NOT NULL THEN ' (' || num_posti::text || ')'
                    ELSE ''
                END,
                CASE
                    WHEN sede IS NOT NULL AND BTRIM(sede) <> '' THEN ', ' || BTRIM(sede)
                    ELSE ''
                END
            )
        )
        """
    )
    op.alter_column("exams", "short_title", nullable=False)


def downgrade() -> None:
    op.drop_column("exams", "short_title")
    op.drop_column("exams", "sede")
