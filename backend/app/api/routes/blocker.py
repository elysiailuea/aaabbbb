from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from backend.app.api.deps import get_db
from backend.app.models.ban import BanRecord
from backend.app.services.settings import get_str, DEFAULTS

router = APIRouter(prefix="/api/blocker", tags=["blocker"])


@router.get("/bans/active")
def active_bans(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    rows = db.execute(
        select(BanRecord).where(and_(BanRecord.status == "active", BanRecord.expires_at > now))
    ).scalars().all()

    return {
        "generated_at": now.isoformat(),
        "bans": [
            {"id": r.id, "src_ip": r.src_ip, "expires_at": r.expires_at.isoformat(), "level": r.level, "reason": r.reason}
            for r in rows
        ],
    }


@router.get("/settings")
def blocker_settings(db: Session = Depends(get_db)):
    wl = get_str(db, "block_whitelist_csv", DEFAULTS["block_whitelist_csv"][1])
    return {"block_whitelist_csv": wl}