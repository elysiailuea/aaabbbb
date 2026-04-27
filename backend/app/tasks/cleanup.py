from datetime import datetime, timedelta, timezone
from sqlalchemy import delete

from backend.app.core.celery_app import celery_app
from backend.app.core.database import SessionLocal
from backend.app.models.event import Event
from backend.app.models.audit import AuditLog


@celery_app.task
def cleanup_old_events(days: int = 7):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    db = SessionLocal()
    try:
        stmt = delete(Event).where(Event.ts < cutoff)
        res = db.execute(stmt)
        db.add(
            AuditLog(
                actor="system",
                action="events.cleanup",
                detail={"days": days, "cutoff": cutoff.isoformat(), "deleted_rows": getattr(res, "rowcount", None)},
            )
        )
        db.commit()
        return {"ok": True, "deleted": getattr(res, "rowcount", None)}
    finally:
        db.close()