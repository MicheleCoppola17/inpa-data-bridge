"""create exams table

Revision ID: 20260303_0001
Revises:
Create Date: 2026-03-03 20:20:00
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260303_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "exams",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("codice", sa.Text(), nullable=False),
        sa.Column("titolo", sa.Text(), nullable=False),
        sa.Column("descrizione", sa.Text(), nullable=False),
        sa.Column("figura_ricercata", sa.Text(), nullable=True),
        sa.Column("data_pubblicazione", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_scadenza", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tipo_procedura", sa.Text(), nullable=True),
        sa.Column("num_posti", sa.Integer(), nullable=True),
        sa.Column("salary_min", sa.Numeric(12, 2), nullable=True),
        sa.Column("salary_max", sa.Numeric(12, 2), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_expired", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_exams_data_pubblicazione", "exams", ["data_pubblicazione"])
    op.create_index("idx_exams_data_scadenza", "exams", ["data_scadenza"])
    op.create_index("idx_exams_last_seen_at", "exams", ["last_seen_at"])
    op.create_index("idx_exams_is_expired", "exams", ["is_expired"])


def downgrade() -> None:
    op.drop_index("idx_exams_is_expired", table_name="exams")
    op.drop_index("idx_exams_last_seen_at", table_name="exams")
    op.drop_index("idx_exams_data_scadenza", table_name="exams")
    op.drop_index("idx_exams_data_pubblicazione", table_name="exams")
    op.drop_table("exams")
