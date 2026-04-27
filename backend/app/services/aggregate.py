from collections import Counter
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from backend.app.models.event import Event
from backend.app.models.profile import AttackerProfile
from backend.app.services.fingerprint import make_http_fingerprint, make_ssh_fingerprint
from backend.app.services.scoring import score_profile
from backend.app.services.settings import get_csv_list, DEFAULTS


def _top(counter: Counter, n: int = 10) -> dict:
    return {k: v for k, v in counter.most_common(n)}


def aggregate_profiles(db: Session, window_minutes: int = 60) -> list[AttackerProfile]:
    now = datetime.now(timezone.utc)
    since = now - timedelta(minutes=window_minutes)
    sensitive_paths = get_csv_list(db, "sensitive_paths_csv", DEFAULTS["sensitive_paths_csv"][1])

    ips = db.execute(select(Event.src_ip).where(Event.ts >= since).group_by(Event.src_ip)).scalars().all()
    updated: list[AttackerProfile] = []

    for ip in ips:
        events = db.execute(
            select(Event).where(and_(Event.src_ip == ip, Event.ts >= since)).order_by(Event.ts.asc())
        ).scalars().all()
        if not events:
            continue

        first_seen = min(e.ts for e in events)
        last_seen = max(e.ts for e in events)

        http_events = [e for e in events if e.protocol == "http" and e.event_type == "http_request"]
        ssh_events = [e for e in events if e.protocol == "ssh" and e.event_type == "ssh_login_attempt"]

        path_counter = Counter([e.payload.get("path", "") for e in http_events if e.payload])
        user_counter = Counter([e.payload.get("username", "") for e in ssh_events if e.payload])

        http_count = len(http_events)
        ssh_fail = sum(1 for e in ssh_events if (e.payload or {}).get("auth_result") == "failed")

        minute_buckets = Counter()
        for e in events:
            minute = e.ts.replace(second=0, microsecond=0)
            minute_buckets[minute] += 1
        peak_rpm = max(minute_buckets.values()) if minute_buckets else 0

        top_paths_list = [k for k, _ in path_counter.most_common(10) if k]
        top_users_list = [k for k, _ in user_counter.most_common(10) if k]

        ua = ""
        if http_events:
            ua_counter = Counter([(e.payload or {}).get("ua", "") for e in http_events])
            ua = ua_counter.most_common(1)[0][0] if ua_counter else ""

        fp_parts = []
        if http_events:
            fp_parts.append(make_http_fingerprint(ua, top_paths_list, peak_rpm))
        if ssh_events:
            fp_parts.append(make_ssh_fingerprint(top_users_list, peak_rpm))
        fingerprint = "|".join(fp_parts)

        score, level, reasons = score_profile(
            http_count, ssh_fail, peak_rpm, top_paths_list, top_users_list, sensitive_paths=sensitive_paths
        )

        prof = db.execute(select(AttackerProfile).where(AttackerProfile.src_ip == ip)).scalar_one_or_none()
        if not prof:
            prof = AttackerProfile(src_ip=ip, first_seen=first_seen, last_seen=last_seen)
            db.add(prof)

        prof.first_seen = min(prof.first_seen, first_seen) if prof.first_seen else first_seen
        prof.last_seen = last_seen
        prof.http_count_1h = http_count
        prof.ssh_fail_count_1h = ssh_fail
        prof.peak_rpm_1h = peak_rpm
        prof.top_paths = _top(path_counter)
        prof.top_usernames = _top(user_counter)
        prof.fingerprint = fingerprint
        prof.risk_score = score
        prof.risk_level = level
        prof.risk_reasons = {"reasons": reasons}

        updated.append(prof)

    db.commit()
    return updated