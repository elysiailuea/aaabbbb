from fastapi import Request, HTTPException, Depends

from backend.app.api.redis_client import client
from backend.app.api.deps import require_user


def _key(request: Request, user: dict | None):
    ip = request.client.host if request.client else "unknown"
    if user:
        return f"rl:{user.get('sub','anon')}:{ip}:{request.url.path}"
    return f"rl:anon:{ip}:{request.url.path}"


def rate_limit(max_requests: int, window_sec: int, authenticated: bool = True):
    """
    简单固定窗口限流：
    - 已登录：按 user+ip+path
    - 未登录：按 ip+path
    """
    async def _dep(request: Request, user: dict = Depends(require_user) if authenticated else None):
        k = _key(request, user)
        n = client.incr(k)
        if n == 1:
            client.expire(k, window_sec)
        if n > max_requests:
            raise HTTPException(status_code=429, detail=f"请求过于频繁：{max_requests}/{window_sec}s")
        return True

    return _dep