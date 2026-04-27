from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.api.deps import get_db, require_user
from backend.app.models.audit import AuditLog

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("")
def list_audit(
    limit: int = Query(200, ge=1, le=1000),
    actor: str | None = None,
    action: str | None = None,
    user=Depends(require_user),
    db: Session = Depends(get_db),
):
    stmt = select(AuditLog).order_by(AuditLog.ts.desc()).limit(limit)
    rows = db.execute(stmt).scalars().all()

    if actor:
        rows = [r for r in rows if r.actor == actor]
    if action:
        rows = [r for r in rows if r.action == action]

    return [{"id": r.id, "ts": r.ts, "actor": r.actor, "action": r.action, "detail": r.detail} for r in rows]