from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db, require_user
from backend.app.core.security import create_access_token, verify_password
from backend.app.models.user import User
from backend.app.schemas.auth import LoginReq, TokenResp

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResp)
def login(req: LoginReq, db: Session = Depends(get_db)):
    user = db.get(User, req.username)
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return TokenResp(access_token=create_access_token(sub=user.username, role=user.role))


@router.get("/me")
def me(claims: dict = Depends(require_user), db: Session = Depends(get_db)):
    return {"username": claims.get("sub", ""), "role": claims.get("role", "")}