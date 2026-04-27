from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.api.deps import get_db, require_user
from backend.app.models.profile import AttackerProfile

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


@router.get("")
def list_profiles(user=Depends(require_user), db: Session = Depends(get_db)):
    rows = db.execute(select(AttackerProfile).order_by(AttackerProfile.last_seen.desc()).limit(200)).scalars().all()
    return [
        {
            "src_ip": r.src_ip,
            "first_seen": r.first_seen,
            "last_seen": r.last_seen,
            "http_count_1h": r.http_count_1h,
            "ssh_fail_count_1h": r.ssh_fail_count_1h,
            "peak_rpm_1h": r.peak_rpm_1h,
            "top_paths": r.top_paths,
            "top_usernames": r.top_usernames,
            "fingerprint": r.fingerprint,
            "risk_score": r.risk_score,
            "risk_level": r.risk_level,
            "risk_reasons": (r.risk_reasons or {}).get("reasons", []),
        }
        for r in rows
    ]


@router.get("/{ip}")
def get_profile(ip: str, user=Depends(require_user), db: Session = Depends(get_db)):
    r = db.execute(select(AttackerProfile).where(AttackerProfile.src_ip == ip)).scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="未找到该 IP 的画像")
    return {
        "src_ip": r.src_ip,
        "first_seen": r.first_seen,
        "last_seen": r.last_seen,
        "http_count_1h": r.http_count_1h,
        "ssh_fail_count_1h": r.ssh_fail_count_1h,
        "peak_rpm_1h": r.peak_rpm_1h,
        "top_paths": r.top_paths,
        "top_usernames": r.top_usernames,
        "fingerprint": r.fingerprint,
        "risk_score": r.risk_score,
        "risk_level": r.risk_level,
        "risk_reasons": (r.risk_reasons or {}).get("reasons", []),
    }