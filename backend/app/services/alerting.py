from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from backend.app.models.profile import AttackerProfile
from backend.app.models.alert import Alert
from backend.app.models.ban import BanRecord
from backend.app.models.audit import AuditLog
from backend.app.services.settings import get_bool, get_int, DEFAULTS


def _make_alert_from_profile(p: AttackerProfile) -> tuple[str, str, str, dict]:
    if p.risk_level in ("critical", "high"):
        alert_type = "attacker.high_risk"
        level = "critical" if p.risk_level == "critical" else "high"
        title = f"高风险攻击者：{p.src_ip}"
        evidence = {
            "risk_score": p.risk_score,
            "risk_level": p.risk_level,
            "risk_reasons": (p.risk_reasons or {}).get("reasons", []),
            "peak_rpm_1h": p.peak_rpm_1h,
            "http_count_1h": p.http_count_1h,
            "ssh_fail_count_1h": p.ssh_fail_count_1h,
            "top_paths": p.top_paths,
            "top_usernames": p.top_usernames,
        }
        return alert_type, level, title, evidence
    return "", "", "", {}


def upsert_dedup_alert(
    db: Session,
    src_ip: str,
    fingerprint: str,
    alert_type: str,
    level: str,
    title: str,
    evidence: dict,
    window_minutes: int = 10,
) -> Alert:
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=window_minutes)

    existing = db.execute(
        select(Alert).where(
            and_(
                Alert.src_ip == src_ip,
                Alert.alert_type == alert_type,
                Alert.fingerprint == fingerprint,
                Alert.window_end >= window_start,
                Alert.status.in_(["open", "ack"]),
            )
        )
    ).scalar_one_or_none()

    if existing:
        existing.hit_count += 1
        existing.window_end = now
        existing.level = level
        existing.evidence = evidence
        db.commit()
        return existing

    a = Alert(
        src_ip=src_ip,
        alert_type=alert_type,
        level=level,
        title=title,
        description="基于画像评分自动生成",
        fingerprint=fingerprint,
        window_start=now,
        window_end=now,
        hit_count=1,
        status="open",
        evidence=evidence,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def ensure_critical_ban(db: Session, p: AttackerProfile) -> BanRecord | None:
    enabled = get_bool(db, "auto_ban_enabled", DEFAULTS["auto_ban_enabled"][1])
    if not enabled or p.risk_level != "critical":
        return None

    ttl_seconds = get_int(db, "auto_ban_ttl_seconds", DEFAULTS["auto_ban_ttl_seconds"][1])
    now = datetime.now(timezone.utc)

    existing = db.execute(
        select(BanRecord).where(
            and_(BanRecord.src_ip == p.src_ip, BanRecord.status == "active", BanRecord.expires_at > now)
        )
    ).scalar_one_or_none()
    if existing:
        return existing

    rec = BanRecord(
        src_ip=p.src_ip,
        reason="auto:critical_risk",
        level="critical",
        status="active",
        created_at=now,
        expires_at=now + timedelta(seconds=ttl_seconds),
        evidence={
            "risk_score": p.risk_score,
            "risk_level": p.risk_level,
            "fingerprint": p.fingerprint,
            "risk_reasons": (p.risk_reasons or {}).get("reasons", []),
        },
        created_by="system",
    )
    db.add(rec)
    db.add(AuditLog(actor="system", action="ban.create", detail={"src_ip": p.src_ip, "reason": rec.reason}))
    db.commit()
    return rec


def process_profiles_to_alerts_and_bans(db: Session):
    window_minutes = get_int(db, "alert_window_minutes", DEFAULTS["alert_window_minutes"][1])

    profiles = db.execute(select(AttackerProfile).order_by(AttackerProfile.last_seen.desc()).limit(200)).scalars().all()
    for p in profiles:
        alert_type, level, title, evidence = _make_alert_from_profile(p)
        if not alert_type:
            continue
        upsert_dedup_alert(db, p.src_ip, p.fingerprint, alert_type, level, title, evidence, window_minutes=window_minutes)
        ensure_critical_ban(db, p)