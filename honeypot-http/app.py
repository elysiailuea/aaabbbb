import os
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, Request

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
INSTANCE_ID = os.getenv("HONEYPOT_INSTANCE_ID", "hp-http-1")

app = FastAPI(title="HTTP Honeypot")


async def emit(ev: dict):
    async with httpx.AsyncClient(timeout=2.0) as client:
        try:
            await client.post(f"{BACKEND_URL}/api/events", json=ev)
        except Exception:
            pass


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def catch_all(full_path: str, request: Request):
    ua = request.headers.get("user-agent", "")
    src_ip = request.client.host if request.client else "unknown"
    qs = str(request.url.query) if request.url.query else ""

    ev = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "src_ip": src_ip,
        "src_port": request.client.port if request.client else None,
        "protocol": "http",
        "event_type": "http_request",
        "payload": {"method": request.method, "path": "/" + full_path, "query": qs, "ua": ua, "status": 200},
        "honeypot": {"name": "honeypot-http", "instance_id": INSTANCE_ID},
    }
    await emit(ev)
    return {"ok": True, "path": "/" + full_path}