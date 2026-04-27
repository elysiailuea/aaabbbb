from __future__ import annotations

import os
import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

# decode_responses=True -> 返回 str，方便调试
client = redis.Redis.from_url(REDIS_URL, decode_responses=True)