"""initial tables

Revision ID: 0001_initial
Revises:
Create Date: 2025-12-25
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("username", sa.String(length=64), primary_key=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
    )

    op.create_table(
        "events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("src_ip", sa.String(length=64), nullable=False),
        sa.Column("src_port", sa.Integer(), nullable=True),
        sa.Column("protocol", sa.String(length=16), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("honeypot_name", sa.String(length=64), nullable=False),
        sa.Column("honeypot_instance_id", sa.String(length=64), nullable=False),
    )
    op.create_index("ix_events_ts", "events", ["ts"])
    op.create_index("ix_events_src_ip", "events", ["src_ip"])
    op.create_index("ix_events_protocol", "events", ["protocol"])
    op.create_index("ix_events_event_type", "events", ["event_type"])
    op.create_index("ix_events_src_ip_ts", "events", ["src_ip", "ts"])
    op.create_index("ix_events_protocol_ts", "events", ["protocol", "ts"])

    op.create_table(
        "attacker_profiles",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("src_ip", sa.String(length=64), nullable=False, unique=True),
        sa.Column("first_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("http_count_1h", sa.Integer(), nullable=False),
        sa.Column("ssh_fail_count_1h", sa.Integer(), nullable=False),
        sa.Column("peak_rpm_1h", sa.Integer(), nullable=False),
        sa.Column("top_paths", sa.JSON(), nullable=False),
        sa.Column("top_usernames", sa.JSON(), nullable=False),
        sa.Column("fingerprint", sa.String(length=128), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("risk_level", sa.String(length=16), nullable=False),
    )
    op.create_index("ix_attacker_profiles_src_ip", "attacker_profiles", ["src_ip"])
    op.create_index("ix_attacker_profiles_last_seen", "attacker_profiles", ["last_seen"])

    op.create_table(
        "alerts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("src_ip", sa.String(length=64), nullable=False),
        sa.Column("alert_type", sa.String(length=64), nullable=False),
        sa.Column("level", sa.String(length=16), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=False),
        sa.Column("fingerprint", sa.String(length=128), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("hit_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
    )
    op.create_index("ix_alerts_src_ip", "alerts", ["src_ip"])
    op.create_index("ix_alerts_alert_type", "alerts", ["alert_type"])
    op.create_index("ix_alerts_fingerprint", "alerts", ["fingerprint"])
    op.create_index("ix_alerts_window_end", "alerts", ["window_end"])
    op.create_index("ix_alerts_src_ip_window_end", "alerts", ["src_ip", "window_end"])

    op.create_table(
        "ban_records",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("src_ip", sa.String(length=64), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("level", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=False),
    )
    op.create_index("ix_ban_records_src_ip", "ban_records", ["src_ip"])
    op.create_index("ix_ban_records_created_at", "ban_records", ["created_at"])
    op.create_index("ix_ban_records_expires_at", "ban_records", ["expires_at"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actor", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("detail", sa.JSON(), nullable=False),
    )
    op.create_index("ix_audit_logs_ts", "audit_logs", ["ts"])
    op.create_index("ix_audit_logs_actor", "audit_logs", ["actor"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("ban_records")
    op.drop_table("alerts")
    op.drop_table("attacker_profiles")
    op.drop_table("events")
    op.drop_table("users")