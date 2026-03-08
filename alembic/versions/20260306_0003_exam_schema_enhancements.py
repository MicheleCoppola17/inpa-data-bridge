"""exam schema enhancements for location and simplified fields

Revision ID: 20260306_0003
Revises: 25640645e19a
Create Date: 2026-03-06 11:15:00
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260306_0003"
down_revision: str | None = "25640645e19a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("exams", "sede", new_column_name="municipality")
    op.add_column("exams", sa.Column("region", sa.Text(), nullable=True))
    op.add_column("exams", sa.Column("province", sa.Text(), nullable=True))
    op.add_column("exams", sa.Column("salary_range", sa.Text(), nullable=True))
    op.add_column("exams", sa.Column("url", sa.Text(), nullable=True))
    op.add_column("exams", sa.Column("selection_criteria", postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    op.execute(
        """
        UPDATE exams
        SET
            url = 'https://www.inpa.gov.it/bandi-e-avvisi/dettaglio-bando-avviso/?concorso_id=' || id,
            salary_range = CASE
                WHEN salary_min IS NOT NULL AND salary_max IS NOT NULL THEN
                    '€' || regexp_replace(to_char(salary_min, 'FM999,999,999,990.00'), '\\.00$', '') ||
                    ' - €' || regexp_replace(to_char(salary_max, 'FM999,999,999,990.00'), '\\.00$', '')
                WHEN salary_min IS NOT NULL THEN
                    'Da €' || regexp_replace(to_char(salary_min, 'FM999,999,999,990.00'), '\\.00$', '')
                WHEN salary_max IS NOT NULL THEN
                    'Fino a €' || regexp_replace(to_char(salary_max, 'FM999,999,999,990.00'), '\\.00$', '')
                ELSE NULL
            END,
            selection_criteria = CASE
                WHEN tipo_procedura IS NULL OR btrim(tipo_procedura) = '' THEN '[]'::jsonb
                ELSE to_jsonb(
                    array_remove(
                        ARRAY[
                            CASE WHEN tipo_procedura ~* '(^|_)TITOLI?(_|$)' THEN 'Titoli' END,
                            CASE WHEN tipo_procedura ~* '(^|_)COLLOQUIO(_|$)' THEN 'Colloquio' END,
                            CASE WHEN tipo_procedura ~* '(^|_)ESAMI?(_|$)' THEN 'Esami' END,
                            CASE
                                WHEN NOT (
                                    tipo_procedura ~* '(^|_)TITOLI?(_|$)'
                                    OR tipo_procedura ~* '(^|_)COLLOQUIO(_|$)'
                                    OR tipo_procedura ~* '(^|_)ESAMI?(_|$)'
                                )
                                THEN 'Altro'
                            END
                        ],
                        NULL
                    )
                )
            END
        """
    )

    op.alter_column("exams", "url", nullable=False)
    op.alter_column("exams", "selection_criteria", nullable=False)


def downgrade() -> None:
    op.drop_column("exams", "selection_criteria")
    op.drop_column("exams", "url")
    op.drop_column("exams", "salary_range")
    op.drop_column("exams", "province")
    op.drop_column("exams", "region")
    op.alter_column("exams", "municipality", new_column_name="sede")
