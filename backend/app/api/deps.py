from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.core.security import decode_token


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


bearer = HTTPBearer(auto_error=False)


def require_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    if not creds:
        raise HTTPException(status_code=401, detail="缺少 Token")
    try:
        return decode_token(creds.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Token 无效或已过期")


def require_role(*allowed: str):
    def _inner(user: dict = Depends(require_user)) -> dict:
        role = user.get("role", "")
        if role not in allowed:
            raise HTTPException(status_code=403, detail=f"权限不足（role={role}）")
        return user

    return _inner