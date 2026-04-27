import random
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import delete

from backend.app.api.deps import get_db, require_role
from backend.app.models.event import Event
from backend.app.models.audit import AuditLog
from backend.app.models.profile import AttackerProfile
from backend.app.models.alert import Alert
from backend.app.models.ban import BanRecord
from backend.app.tasks.jobs import run_aggregation_and_alerts

router = APIRouter(prefix="/api/demo", tags=["demo"])

SAMPLE_IPS = ["203.0.113.10", "203.0.113.11", "198.51.100.8", "198.51.100.9", "192.0.2.77"]
SENSITIVE_PATHS = ["/.env", "/.git/config", "/wp-login.php", "/phpmyadmin", "/admin", "/xmlrpc.php"]
UA_POOL = ["zgrab/0.x", "masscan/1.3", "python-requests/2.x", "curl/8.x", "sqlmap/1.7"]


def _now():
    return datetime.now(timezone.utc)


@router.post("/seed")
def seed_demo_data(body: dict | None = None, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    body = body or {}
    minutes = int(body.get("minutes", 30))
    http_events = int(body.get("http_events", 200))
    ssh_events = int(body.get("ssh_events", 60))
    ip = body.get("ip")

    ips = [ip] if ip else random.sample(SAMPLE_IPS, k=2)
    now = _now()
    start = now - timedelta(minutes=minutes)

    created = 0

    for _ in range(http_events):
        src_ip = random.choice(ips)
        ts = start + timedelta(seconds=random.randint(0, minutes * 60))
        path = random.choice(SENSITIVE_PATHS + ["/", "/login", "/api", "/robots.txt", "/favicon.ico"])
        ua = random.choice(UA_POOL)

        db.add(
            Event(
                ts=ts,
                src_ip=src_ip,
                src_port=random.randint(20000, 65000),
                protocol="http",
                event_type="http_request",
                payload={"method": "GET", "path": path, "query": "", "ua": ua, "status": 404 if path != "/" else 200},
                honeypot_name="honeypot-http",
                honeypot_instance_id="demo-http",
            )
        )
        created += 1

    usernames = ["root", "admin", "test", "oracle", "ubuntu"]
    for _ in range(ssh_events):
        src_ip = random.choice(ips)
        ts = start + timedelta(seconds=random.randint(0, minutes * 60))
        u = random.choice(usernames)
        db.add(
            Event(
                ts=ts,
                src_ip=src_ip,
                src_port=random.randint(20000, 65000),
                protocol="ssh",
                event_type="ssh_login_attempt",
                payload={
                    "username": u,
                    "password_masked": "p******d",
                    "password_hash": "",
                    "auth_result": "failed",
                    "client_version": "libssh-0.10",
                },
                honeypot_name="cowrie",
                honeypot_instance_id="demo-ssh",
            )
        )
        created += 1

    db.add(AuditLog(actor=user["sub"], action="demo.seed", detail={"ips": ips, "created": created, "minutes": minutes}))
    db.commit()

    run_aggregation_and_alerts.delay()

    return {"ok": True, "created": created, "ips": ips, "note": "已写入模拟事件并触发聚合任务（稍等 5~30 秒查看看板/告警）。"}


@router.post("/purge")
def purge_demo_data(body: dict | None = None, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    body = body or {}
    ips = body.get("ips") or SAMPLE_IPS
    purge_profiles = bool(body.get("purge_profiles", True))
    purge_alerts = bool(body.get("purge_alerts", True))
    purge_bans = bool(body.get("purge_bans", False))

    res_events = db.execute(delete(Event).where(Event.honeypot_instance_id.in_(["demo-http", "demo-ssh"])))

    deleted_profiles = 0
    deleted_alerts = 0
    deleted_bans = 0

    if purge_profiles:
        r = db.execute(delete(AttackerProfile).where(AttackerProfile.src_ip.in_(ips)))
        deleted_profiles = getattr(r, "rowcount", 0) or 0

    if purge_alerts:
        r = db.execute(delete(Alert).where(Alert.src_ip.in_(ips)))
        deleted_alerts = getattr(r, "rowcount", 0) or 0

    if purge_bans:
        r = db.execute(delete(BanRecord).where(BanRecord.src_ip.in_(ips)))
        deleted_bans = getattr(r, "rowcount", 0) or 0

    db.execute(delete(AuditLog).where(AuditLog.action.in_(["demo.seed", "demo.purge"])))

    db.add(
        AuditLog(
            actor=user["sub"],
            action="demo.purge",
            detail={
                "ips": ips,
                "events_deleted": getattr(res_events, "rowcount", None),
                "profiles_deleted": deleted_profiles,
                "alerts_deleted": deleted_alerts,
                "bans_deleted": deleted_bans,
                "purge_bans": purge_bans,
            },
        )
    )
    db.commit()

    return {
        "ok": True,
        "events_deleted": getattr(res_events, "rowcount", None),
        "profiles_deleted": deleted_profiles,
        "alerts_deleted": deleted_alerts,
        "bans_deleted": deleted_bans,
        "note": "已清理演示数据。默认不删封禁；可手动解封或等待 TTL 到期。",
    }