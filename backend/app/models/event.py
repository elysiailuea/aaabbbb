from sqlalchemy import String, DateTime, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
import uuid

from backend.app.core.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    src_ip: Mapped[str] = mapped_column(String(64), index=True)
    src_port: Mapped[int | None] = mapped_column(nullable=True)
    protocol: Mapped[str] = mapped_column(String(16), index=True)  # http/ssh
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    honeypot_name: Mapped[str] = mapped_column(String(64), default="unknown")
    honeypot_instance_id: Mapped[str] = mapped_column(String(64), default="unknown")

    __table_args__ = (
        Index("ix_events_src_ip_ts", "src_ip", "ts"),
        Index("ix_events_protocol_ts", "protocol", "ts"),
    )