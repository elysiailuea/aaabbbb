"""settings table

Revision ID: 0002_settings
Revises: 0001_initial
Create Date: 2025-12-25
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_settings"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "settings",
        sa.Column("key", sa.String(length=64), primary_key=True),
        sa.Column("int_value", sa.Integer(), nullable=True),
        sa.Column("str_value", sa.String(length=255), nullable=True),
        sa.Column("bool_value", sa.Boolean(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("settings")