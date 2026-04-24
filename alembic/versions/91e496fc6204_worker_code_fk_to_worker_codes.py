"""worker_code_fk_to_worker_codes

Revision ID: 91e496fc6204
Revises: 7b91d069aa7b
Create Date: 2026-04-24 10:35:51.892083

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91e496fc6204'
down_revision: Union[str, Sequence[str], None] = '7b91d069aa7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('workers', 'worker_code')
    op.add_column('workers', sa.Column('worker_code', sa.Uuid(), nullable=False))
    op.create_foreign_key('fk_workers_worker_code', 'workers', 'worker_codes', ['worker_code'], ['code_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_workers_worker_code', 'workers', type_='foreignkey')
    op.drop_column('workers', 'worker_code')
    op.add_column('workers', sa.Column('worker_code', sa.VARCHAR(length=50), nullable=False))
    # ### end Alembic commands ###
