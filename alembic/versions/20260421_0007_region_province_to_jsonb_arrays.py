"""Convert region/province text columns to regions/provinces JSONB arrays.

Revision ID: 20260421_0007
Revises: f3c6f6749e81
Create Date: 2026-04-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "20260421_0007"
down_revision = "20260321_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add new JSONB columns with defaults
    op.add_column("exams", sa.Column("regions", JSONB, nullable=False, server_default="[]"))
    op.add_column("exams", sa.Column("provinces", JSONB, nullable=False, server_default="[]"))

    # 2. Migrate existing data: wrap single values into arrays
    op.execute("""
        UPDATE exams
        SET regions = CASE
                WHEN region IS NOT NULL THEN jsonb_build_array(region)
                ELSE '[]'::jsonb
            END,
            provinces = CASE
                WHEN province IS NOT NULL THEN jsonb_build_array(province)
                ELSE '[]'::jsonb
            END
    """)

    # 3. Drop old columns
    op.drop_column("exams", "region")
    op.drop_column("exams", "province")

    # 4. Remove server defaults (no longer needed after migration)
    op.alter_column("exams", "regions", server_default=None)
    op.alter_column("exams", "provinces", server_default=None)


def downgrade() -> None:
    # Re-create old text columns
    op.add_column("exams", sa.Column("region", sa.Text, nullable=True))
    op.add_column("exams", sa.Column("province", sa.Text, nullable=True))

    # Extract first element from arrays
    op.execute("""
        UPDATE exams
        SET region = regions->>0,
            province = provinces->>0
    """)

    # Drop JSONB columns
    op.drop_column("exams", "regions")
    op.drop_column("exams", "provinces")
