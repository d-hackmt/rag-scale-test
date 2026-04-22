import redis
import json
import logfire
from app.config import REDIS_HOST, REDIS_PORT

# Initialize Redis Client
# Note: This will only connect if the application is running in the same VPC as Memorystore
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        socket_timeout=1 # Fast timeout for local dev
    )
    # Quick check to see if we can actually reach the server
    redis_client.ping()
    print("🚀 Redis Connected (Caching Enabled)")
except Exception:
    print("ℹ️ Redis unreachable (Local mode - Caching disabled)")
    redis_client = None

def get_cache(key: str):
    """Retrieves a value from Redis cache."""
    if not redis_client:
        return None
    try:
        data = redis_client.get(key)
        if data:
            with logfire.span("Redis Cache Hit"):
                return json.loads(data)
        return None
    except Exception as e:
        print(f"Redis Get Error: {e}")
        return None

def set_cache(key: str, value: dict, ttl: int = 3600):
    """Sets a value in Redis cache with a TTL (default 1 hour)."""
    if not redis_client:
        return
    try:
        with logfire.span("Redis Cache Set"):
            redis_client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        print(f"Redis Set Error: {e}")

def get_session_history(session_id: str):
    """Retrieves chat history for a specific session."""
    if not redis_client:
        return []
    try:
        history = redis_client.lrange(f"history:{session_id}", 0, -1)
        return [json.loads(m) for m in history]
    except Exception as e:
        print(f"Redis History Get Error: {e}")
        return []

def add_to_history(session_id: str, message: dict):
    """Adds a message to the session history (kept for last 10 turns)."""
    if not redis_client:
        return
    try:
        key = f"history:{session_id}"
        redis_client.rpush(key, json.dumps(message))
        redis_client.ltrim(key, -10, -1) # Keep only the last 10 messages
        redis_client.expire(key, 86400) # Expire history after 24 hours
    except Exception as e:
        print(f"Redis History Add Error: {e}")
