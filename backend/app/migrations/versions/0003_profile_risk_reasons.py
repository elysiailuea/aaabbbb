"""add risk_reasons to attacker_profiles

Revision ID: 0003_profile_risk_reasons
Revises: 0002_settings
Create Date: 2025-12-25
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_profile_risk_reasons"
down_revision = "0002_settings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PostgreSQL: '{}'::json
    op.add_column(
        "attacker_profiles",
        sa.Column("risk_reasons", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
    )


def downgrade() -> None:
    op.drop_column("attacker_profiles", "risk_reasons")