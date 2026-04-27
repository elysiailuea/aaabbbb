import redis
from backend.app.core.config import settings

client = redis.Redis.from_url(settings.redis_url, decode_responses=True)