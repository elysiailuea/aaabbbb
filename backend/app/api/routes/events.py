import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.api.deps import get_db, require_user
from backend.app.models.event import Event
from backend.app.schemas.event import EventIn
from backend.app.services.settings import get_csv_list, DEFAULTS

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("")
def ingest_event(ev: EventIn, db: Session = Depends(get_db)):
    row = Event(
        ts=ev.ts,
        src_ip=ev.src_ip,
        src_port=ev.src_port,
        protocol=ev.protocol,
        event_type=ev.event_type,
        payload=ev.payload,
        honeypot_name=ev.honeypot.name,
        honeypot_instance_id=ev.honeypot.instance_id,
    )
    db.add(row)
    db.commit()
    return {"ok": True, "id": row.id}


def _apply_payload_filters(
    rows: list[Event],
    *,
    path: str | None,
    ua_contains: str | None,
    ssh_user: str | None,
    auth_result: str | None,
    sensitive_only: bool,
    sensitive_paths: list[str],
):
    if sensitive_only:
        rows = [r for r in rows if r.protocol == "http" and (r.payload or {}).get("path") in sensitive_paths]

    if path:
        rows = [r for r in rows if (r.payload or {}).get("path") == path]

    if ua_contains:
        u = ua_contains.lower()
        rows = [r for r in rows if ((r.payload or {}).get("ua", "") or "").lower().find(u) >= 0]

    if ssh_user:
        rows = [
            r
            for r in rows
            if r.protocol == "ssh"
            and r.event_type == "ssh_login_attempt"
            and (r.payload or {}).get("username") == ssh_user
        ]

    if auth_result:
        rows = [
            r
            for r in rows
            if r.protocol == "ssh"
            and r.event_type == "ssh_login_attempt"
            and (r.payload or {}).get("auth_result") == auth_result
        ]

    return rows


@router.get("/search")
def search_events(
    protocol: str | None = None,
    event_type: str | None = None,
    src_ip: str | None = None,
    path: str | None = None,
    ua_contains: str | None = None,
    ssh_user: str | None = None,
    auth_result: str | None = None,
    sensitive_only: bool = False,
    limit: int = Query(200, ge=1, le=2000),
    user=Depends(require_user),
    db: Session = Depends(get_db),
):
    sensitive_paths = get_csv_list(db, "sensitive_paths_csv", DEFAULTS["sensitive_paths_csv"][1])

    stmt = select(Event).order_by(Event.ts.desc()).limit(limit)
    if protocol:
        stmt = stmt.where(Event.protocol == protocol)
    if event_type:
        stmt = stmt.where(Event.event_type == event_type)
    if src_ip:
        stmt = stmt.where(Event.src_ip == src_ip)

    rows = db.execute(stmt).scalars().all()
    rows = _apply_payload_filters(
        rows,
        path=path,
        ua_contains=ua_contains,
        ssh_user=ssh_user,
        auth_result=auth_result,
        sensitive_only=sensitive_only,
        sensitive_paths=sensitive_paths,
    )

    return [
        {
            "id": r.id,
            "ts": r.ts,
            "src_ip": r.src_ip,
            "src_port": r.src_port,
            "protocol": r.protocol,
            "event_type": r.event_type,
            "payload": r.payload,
            "honeypot_name": r.honeypot_name,
            "honeypot_instance_id": r.honeypot_instance_id,
        }
        for r in rows
    ]


@router.get("/export")
def export_events(
    fmt: str = Query("json", pattern="^(json|csv)$"),
    protocol: str | None = None,
    event_type: str | None = None,
    src_ip: str | None = None,
    path: str | None = None,
    ua_contains: str | None = None,
    ssh_user: str | None = None,
    auth_result: str | None = None,
    sensitive_only: bool = False,
    limit: int = Query(500, ge=1, le=5000),
    user=Depends(require_user),
    db: Session = Depends(get_db),
):
    sensitive_paths = get_csv_list(db, "sensitive_paths_csv", DEFAULTS["sensitive_paths_csv"][1])

    stmt = select(Event).order_by(Event.ts.desc()).limit(limit)
    if protocol:
        stmt = stmt.where(Event.protocol == protocol)
    if event_type:
        stmt = stmt.where(Event.event_type == event_type)
    if src_ip:
        stmt = stmt.where(Event.src_ip == src_ip)

    rows = db.execute(stmt).scalars().all()
    rows = _apply_payload_filters(
        rows,
        path=path,
        ua_contains=ua_contains,
        ssh_user=ssh_user,
        auth_result=auth_result,
        sensitive_only=sensitive_only,
        sensitive_paths=sensitive_paths,
    )

    data = [
        {
            "id": r.id,
            "ts": r.ts.isoformat() if hasattr(r.ts, "isoformat") else str(r.ts),
            "src_ip": r.src_ip,
            "src_port": r.src_port,
            "protocol": r.protocol,
            "event_type": r.event_type,
            "path": (r.payload or {}).get("path", ""),
            "method": (r.payload or {}).get("method", ""),
            "ua": (r.payload or {}).get("ua", ""),
            "ssh_username": (r.payload or {}).get("username", ""),
            "ssh_auth_result": (r.payload or {}).get("auth_result", ""),
            "honeypot": f"{r.honeypot_name}:{r.honeypot_instance_id}",
        }
        for r in rows
    ]

    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

    if fmt == "json":
        import json

        buf = io.BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
        return StreamingResponse(
            buf,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="events-{ts}.json"'},
        )

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(data[0].keys()) if data else ["id"])
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    csv_bytes = io.BytesIO(output.getvalue().encode("utf-8"))
    return StreamingResponse(
        csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="events-{ts}.csv"'},
    )