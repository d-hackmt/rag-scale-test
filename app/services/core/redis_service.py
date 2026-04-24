import redis
import json
import logfire
from app.services.core.config import settings

# Initialize Redis Client
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,
        socket_timeout=1 # Fast timeout for local dev resilience
    )
    # Quick check to see if we can actually reach the server
    redis_client.ping()
    logfire.info("✅ Redis Semantic Cache Connected")
except Exception as e:
    logfire.warning(f"⚠️ Redis Connection Skip: {e} (Expected in local dev)")
    redis_client = None

def get_cache(key: str):
    if not redis_client: return None
    data = redis_client.get(key)
    return json.loads(data) if data else None

def set_cache(key: str, value: dict, ttl: int = 3600):
    if not redis_client: return
    redis_client.setex(key, ttl, json.dumps(value))
