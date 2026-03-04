"""add read indexes for exams

Revision ID: 20260304_0002
Revises: 20260303_0001
Create Date: 2026-03-04 11:05:00
"""

from typing import Sequence

from alembic import op

revision: str = "20260304_0002"
down_revision: str | None = "20260303_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index("idx_exams_updated_at", "exams", ["updated_at"])
    op.create_index(
        "idx_exams_expired_pub",
        "exams",
        ["is_expired", "data_pubblicazione"],
    )


def downgrade() -> None:
    op.drop_index("idx_exams_expired_pub", table_name="exams")
    op.drop_index("idx_exams_updated_at", table_name="exams")
