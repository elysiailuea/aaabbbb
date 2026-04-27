from sqlalchemy import String, DateTime, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
import uuid

from backend.app.core.database import Base


class BanRecord(Base):
    __tablename__ = "ban_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    src_ip: Mapped[str] = mapped_column(String(64), index=True)
    reason: Mapped[str] = mapped_column(String(255), default="")
    level: Mapped[str] = mapped_column(String(16), default="high")
    status: Mapped[str] = mapped_column(String(16), default="active")  # active/revoked/expired

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    created_by: Mapped[str] = mapped_column(String(64), default="system")

    __table_args__ = (
        Index("ix_ban_records_created_at", "created_at"),
        Index("ix_ban_records_expires_at", "expires_at"),
    )