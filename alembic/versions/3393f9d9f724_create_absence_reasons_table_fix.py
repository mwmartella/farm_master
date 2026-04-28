"""create_absence_reasons_table_fix
Revision ID: 3393f9d9f724
Revises: 8272d2e0013c
Create Date: 2026-04-29 06:34:32.456407
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
# revision identifiers, used by Alembic.
revision: str = '3393f9d9f724'
down_revision: Union[str, Sequence[str], None] = '8272d2e0013c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade() -> None:
    op.execute(
        "CREATE TABLE IF NOT EXISTS absence_reasons ("
        "id UUID PRIMARY KEY DEFAULT gen_random_uuid(), "
        "name TEXT NOT NULL UNIQUE, "
        "notes TEXT, "
        "created_at TIMESTAMPTZ NOT NULL DEFAULT now(), "
        "updated_at TIMESTAMPTZ NOT NULL DEFAULT now()"
        ")"
    )
def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS absence_reasons")
