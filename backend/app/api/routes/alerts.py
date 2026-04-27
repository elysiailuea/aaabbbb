from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select


from backend.app.api.deps import get_db, require_user, require_role
from backend.app.api.rate_limit import rate_limit
from backend.app.models.alert import Alert
from backend.app.models.audit import AuditLog

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
def list_alerts(user=Depends(require_user), db: Session = Depends(get_db)):
    rows = db.execute(select(Alert).order_by(Alert.window_end.desc()).limit(200)).scalars().all()
    return [
        {
            "id": r.id,
            "src_ip": r.src_ip,
            "alert_type": r.alert_type,
            "level": r.level,
            "title": r.title,
            "status": r.status,
            "hit_count": r.hit_count,
            "window_start": r.window_start,
            "window_end": r.window_end,
            "fingerprint": r.fingerprint,
            "evidence": r.evidence,
        }
        for r in rows
    ]


@router.post("/{alert_id}/ack", dependencies=[Depends(rate_limit(60, 60))])
def ack_alert(alert_id: str, user=Depends(require_role("admin", "operator")), db: Session = Depends(get_db)):
    r = db.get(Alert, alert_id)
    if not r:
        return {"ok": False}
    r.status = "ack"
    db.add(AuditLog(actor=user["sub"], action="alert.ack", detail={"alert_id": alert_id}))
    db.commit()
    return {"ok": True}


@router.post("/{alert_id}/close", dependencies=[Depends(rate_limit(60, 60))])
def close_alert(alert_id: str, user=Depends(require_role("admin", "operator")), db: Session = Depends(get_db)):
    r = db.get(Alert, alert_id)
    if not r:
        return {"ok": False}
    r.status = "closed"
    db.add(AuditLog(actor=user["sub"], action="alert.close", detail={"alert_id": alert_id}))
    db.commit()
    return {"ok": True}