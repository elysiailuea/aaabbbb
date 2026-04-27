from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.api.deps import get_db, require_user, require_role
from backend.app.api.rate_limit import rate_limit
from backend.app.models.ban import BanRecord
from backend.app.schemas.ban import BanCreate, BanOut
from backend.app.models.audit import AuditLog

router = APIRouter(prefix="/api/bans", tags=["bans"])


@router.post("", response_model=BanOut, dependencies=[Depends(rate_limit(20, 60))])
def create_ban(req: BanCreate, user=Depends(require_role("admin", "operator")), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    rec = BanRecord(
        src_ip=req.src_ip,
        reason=req.reason,
        level=req.level,
        status="active",
        created_at=now,
        expires_at=now + timedelta(seconds=req.ttl_seconds),
        evidence=req.evidence,
        created_by=user["sub"],
    )
    db.add(rec)
    db.add(AuditLog(actor=user["sub"], action="ban.create", detail={"src_ip": req.src_ip, "reason": req.reason, "level": req.level}))
    db.commit()
    db.refresh(rec)
    return BanOut(**rec.__dict__)


@router.get("", response_model=list[BanOut])
def list_bans(user=Depends(require_user), db: Session = Depends(get_db)):
    rows = db.execute(select(BanRecord).order_by(BanRecord.created_at.desc())).scalars().all()
    return [BanOut(**r.__dict__) for r in rows]


@router.post("/{ban_id}/revoke", response_model=BanOut, dependencies=[Depends(rate_limit(20, 60))])
def revoke_ban(ban_id: str, user=Depends(require_role("admin", "operator")), db: Session = Depends(get_db)):
    rec = db.get(BanRecord, ban_id)
    if not rec:
        raise HTTPException(status_code=404, detail="未找到该封禁记录")
    rec.status = "revoked"
    db.add(AuditLog(actor=user["sub"], action="ban.revoke", detail={"ban_id": ban_id, "src_ip": rec.src_ip}))
    db.commit()
    db.refresh(rec)
    return BanOut(**rec.__dict__)