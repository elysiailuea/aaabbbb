from sqlalchemy import String, DateTime, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
import uuid

from backend.app.core.database import Base


class AttackerProfile(Base):
    __tablename__ = "attacker_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    src_ip: Mapped[str] = mapped_column(String(64), index=True, unique=True)

    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    http_count_1h: Mapped[int] = mapped_column(Integer, default=0)
    ssh_fail_count_1h: Mapped[int] = mapped_column(Integer, default=0)
    peak_rpm_1h: Mapped[int] = mapped_column(Integer, default=0)

    top_paths: Mapped[dict] = mapped_column(JSON, default=dict)
    top_usernames: Mapped[dict] = mapped_column(JSON, default=dict)

    fingerprint: Mapped[str] = mapped_column(String(128), default="")
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    risk_level: Mapped[str] = mapped_column(String(16), default="low")  # low/medium/high/critical
    risk_reasons: Mapped[dict] = mapped_column(JSON, default=dict)  # {"reasons":[...]}