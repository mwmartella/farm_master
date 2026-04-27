"""create_varieties_table

Revision ID: d4b8e1c73f29
Revises: c7e2a4f91b30
Create Date: 2026-04-27 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "d4b8e1c73f29"
down_revision = "c7e2a4f91b30"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "varieties",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("fruit_type_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["fruit_type_id"], ["fruit_types.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "fruit_type_id"),
    )


def downgrade() -> None:
    op.drop_table("varieties")
