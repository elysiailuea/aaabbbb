from datetime import datetime, timedelta, timezone
from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from backend.app.api.deps import get_db, require_user
from backend.app.models.event import Event
from backend.app.models.alert import Alert
from backend.app.models.ban import BanRecord

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(user=Depends(require_user), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    since_1h = now - timedelta(hours=1)
    since_24h = now - timedelta(hours=24)

    events_1h = db.execute(select(Event).where(Event.ts >= since_1h)).scalars().all()
    events_24h = db.execute(select(Event).where(Event.ts >= since_24h)).scalars().all()

    http_24h = sum(1 for e in events_24h if e.protocol == "http")
    ssh_24h = sum(1 for e in events_24h if e.protocol == "ssh")

    alerts_open = db.execute(select(Alert).where(Alert.status.in_(["open", "ack"]))).scalars().all()
    bans_active = db.execute(
        select(BanRecord).where(and_(BanRecord.status == "active", BanRecord.expires_at > now))
    ).scalars().all()

    # trend per minute for last 60 minutes
    def minute_key(dt):
        return dt.replace(second=0, microsecond=0).isoformat()

    buckets_all = Counter([minute_key(e.ts) for e in events_1h])
    buckets_http = Counter([minute_key(e.ts) for e in events_1h if e.protocol == "http"])
    buckets_ssh = Counter([minute_key(e.ts) for e in events_1h if e.protocol == "ssh"])
    buckets_ssh_fail = Counter(
        [minute_key(e.ts) for e in events_1h if e.protocol == "ssh" and (e.payload or {}).get("auth_result") == "failed"]
    )

    minutes = [minute_key(since_1h + timedelta(minutes=i)) for i in range(61)]
    trend = lambda b: [{"t": m, "count": int(b.get(m, 0))} for m in minutes]

    top_ips = Counter([e.src_ip for e in events_1h]).most_common(10)
    top_paths = Counter([(e.payload or {}).get("path", "") for e in events_1h if e.protocol == "http"]).most_common(10)
    top_uas = Counter([(e.payload or {}).get("ua", "") for e in events_1h if e.protocol == "http"]).most_common(10)
    top_ssh_users = Counter([(e.payload or {}).get("username", "") for e in events_1h if e.protocol == "ssh"]).most_common(10)

    alerts_by_level = Counter([a.level for a in alerts_open]).most_common()

    return {
        "generated_at": now.isoformat(),
        "stats": {
            "events_1h": len(events_1h),
            "events_24h": len(events_24h),
            "http_24h": http_24h,
            "ssh_24h": ssh_24h,
            "alerts_open": len(alerts_open),
            "bans_active": len(bans_active),
        },
        "trend": {
            "all": trend(buckets_all),
            "http": trend(buckets_http),
            "ssh": trend(buckets_ssh),
            "ssh_fail": trend(buckets_ssh_fail),
        },
        "top_ips_1h": [{"ip": ip, "count": c} for ip, c in top_ips if ip],
        "top_paths_1h": [{"path": p, "count": c} for p, c in top_paths if p],
        "top_uas_1h": [{"ua": ua, "count": c} for ua, c in top_uas if ua],
        "top_ssh_usernames_1h": [{"username": u, "count": c} for u, c in top_ssh_users if u],
        "alerts_by_level_open": [{"level": lvl, "count": c} for lvl, c in alerts_by_level],
    }