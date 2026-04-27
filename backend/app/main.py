from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.core.config import settings
from backend.app.core.security import hash_password
from backend.app.models.user import User

# ensure models are imported for migrations runtime
from backend.app.models.event import Event  # noqa: F401
from backend.app.models.ban import BanRecord  # noqa: F401
from backend.app.models.profile import AttackerProfile  # noqa: F401
from backend.app.models.alert import Alert  # noqa: F401
from backend.app.models.audit import AuditLog  # noqa: F401
from backend.app.models.settings import Settings  # noqa: F401

from backend.app.services.settings import ensure_defaults

from backend.app.api.routes import (
    auth,
    events,
    profiles,
    alerts,
    bans,
    blocker,
    audit,
    settings as settings_route,
    dashboard,
    report,
    system,
    demo,
)

app = FastAPI(title="蜜罐联动防护平台 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def ensure_users_and_defaults():
    db: Session = SessionLocal()
    try:
        users = [
            ("admin", settings.admin_password, "admin"),
            ("operator", "operator123", "operator"),
            ("viewer", "viewer123", "viewer"),
        ]
        for username, password, role in users:
            u = db.get(User, username)
            if not u:
                db.add(User(username=username, password_hash=hash_password(password), role=role))
        db.commit()

        ensure_defaults(db)
    finally:
        db.close()


ensure_users_and_defaults()

app.include_router(auth.router)
app.include_router(events.router)
app.include_router(profiles.router)
app.include_router(alerts.router)
app.include_router(bans.router)
app.include_router(blocker.router)
app.include_router(audit.router)
app.include_router(settings_route.router)
app.include_router(dashboard.router)
app.include_router(report.router)
app.include_router(system.router)
app.include_router(demo.router)