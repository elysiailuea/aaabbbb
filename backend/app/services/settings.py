from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.settings import Settings as SettingsRow


DEFAULTS = {
    "auto_ban_enabled": ("bool", True),
    "auto_ban_ttl_seconds": ("int", 3600),
    "critical_score_threshold": ("int", 80),
    "high_score_threshold": ("int", 60),
    "alert_window_minutes": ("int", 10),
    "block_whitelist_csv": ("str", "127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"),
    "sensitive_paths_csv": ("str", "/.env,/.git/config,/wp-login.php,/xmlrpc.php,/phpmyadmin,/admin,/config.php"),
}


def ensure_defaults(db: Session):
    keys = list(DEFAULTS.keys())
    existing = {r.key for r in db.execute(select(SettingsRow).where(SettingsRow.key.in_(keys))).scalars().all()}
    for k, (t, v) in DEFAULTS.items():
        if k in existing:
            continue
        row = SettingsRow(key=k)
        if t == "bool":
            row.bool_value = bool(v)
        elif t == "int":
            row.int_value = int(v)
        else:
            row.str_value = str(v)
        db.add(row)
    db.commit()


def get_bool(db: Session, key: str, default: bool) -> bool:
    row = db.get(SettingsRow, key)
    return default if not row or row.bool_value is None else bool(row.bool_value)


def get_int(db: Session, key: str, default: int) -> int:
    row = db.get(SettingsRow, key)
    return default if not row or row.int_value is None else int(row.int_value)


def get_str(db: Session, key: str, default: str) -> str:
    row = db.get(SettingsRow, key)
    return default if not row or row.str_value is None else str(row.str_value)


def get_csv_list(db: Session, key: str, default_csv: str) -> list[str]:
    raw = get_str(db, key, default_csv)
    parts = [p.strip() for p in (raw or "").split(",")]
    return [p for p in parts if p]