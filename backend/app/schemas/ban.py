from pydantic import BaseModel, Field


class BanCreate(BaseModel):
    src_ip: str
    reason: str = "manual"
    level: str = Field(default="high")
    ttl_seconds: int = 3600
    evidence: dict = Field(default_factory=dict)


class BanOut(BaseModel):
    id: str
    src_ip: str
    reason: str
    level: str
    status: str
    created_at: object
    expires_at: object
    created_by: str
    evidence: dict