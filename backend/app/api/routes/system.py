from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, select

from backend.app.api.deps import get_db, require_user
from backend.app.core.redis_client import client as redis_client
from backend.app.models.audit import AuditLog

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/health")
def health():
    return {"ok": True, "ts": datetime.now(timezone.utc).isoformat()}


@router.get("/status")
def status(user=Depends(require_user), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)

    pg_ok = True
    pg_error = ""
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        pg_ok = False
        pg_error = str(e)

    redis_ok = True
    redis_error = ""
    try:
        redis_client.ping()
    except Exception as e:
        redis_ok = False
        redis_error = str(e)

    last_jobs = db.execute(
        select(AuditLog).where(AuditLog.action == "jobs.aggregate").order_by(AuditLog.ts.desc()).limit(1)
    ).scalars().first()

    return {
        "generated_at": now.isoformat(),
        "postgres": {"ok": pg_ok, "error": pg_error},
        "redis": {"ok": redis_ok, "error": redis_error},
        "celery": {"note": "建议通过 docker compose logs 查看 worker/beat；此处用最近聚合时间作为间接指标。"},
        "last_aggregation": None if not last_jobs else {"ts": last_jobs.ts, "detail": last_jobs.detail},
    }