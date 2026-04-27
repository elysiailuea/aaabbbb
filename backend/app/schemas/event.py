from datetime import datetime
from pydantic import BaseModel, Field


class HoneypotRef(BaseModel):
    name: str = "unknown"
    instance_id: str = "unknown"


class EventIn(BaseModel):
    ts: datetime
    src_ip: str
    src_port: int | None = None
    protocol: str = Field(..., pattern="^(http|ssh)$")
    event_type: str
    payload: dict = Field(default_factory=dict)
    honeypot: HoneypotRef = Field(default_factory=HoneypotRef)