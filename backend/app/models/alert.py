from sqlalchemy import String, DateTime, JSON, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
import uuid

from backend.app.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    src_ip: Mapped[str] = mapped_column(String(64), index=True)

    alert_type: Mapped[str] = mapped_column(String(64), index=True)
    level: Mapped[str] = mapped_column(String(16), default="medium")
    title: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(String(1024), default="")

    fingerprint: Mapped[str] = mapped_column(String(128), default="", index=True)

    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    hit_count: Mapped[int] = mapped_column(Integer, default=1)

    status: Mapped[str] = mapped_column(String(16), default="open")
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)

    __table_args__ = (
        Index("ix_alerts_src_ip_window_end", "src_ip", "window_end"),
    )