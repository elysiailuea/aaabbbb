from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.api.deps import get_db, require_user, require_role
from backend.app.models.settings import Settings as SettingsRow
from backend.app.models.audit import AuditLog

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("")
def list_settings(user=Depends(require_user), db: Session = Depends(get_db)):
    rows = db.execute(select(SettingsRow)).scalars().all()
    return [{"key": r.key, "int_value": r.int_value, "str_value": r.str_value, "bool_value": r.bool_value} for r in rows]


@router.put("/{key}")
def update_setting(key: str, body: dict, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    r = db.get(SettingsRow, key)
    if not r:
        r = SettingsRow(key=key)
        db.add(r)

    if "int_value" in body:
        r.int_value = body["int_value"]
    if "str_value" in body:
        r.str_value = body["str_value"]
    if "bool_value" in body:
        r.bool_value = body["bool_value"]

    db.add(AuditLog(actor=user["sub"], action="settings.update", detail={"key": key, "body": body}))
    db.commit()
    return {"ok": True}