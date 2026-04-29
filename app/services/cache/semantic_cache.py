import logfire
from redisvl.extensions.llmcache import SemanticCache
from app.services.core.config import settings

# Global cache holder
_cache = None

def get_semantic_cache():
    """Lazy initialization of the Redis Semantic Cache."""
    global _cache
    if _cache is None and settings.USE_SEMANTIC_CACHE:
        try:
            # We use RedisVL to manage the semantic vector index in Redis
            _cache = SemanticCache(
                name="rag_semantic_cache",
                prefix="cache",
                redis_url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                distance_threshold=0.1 # 0.1 means 90% similar or better
            )
            logfire.info("🚀 Redis Semantic Cache Initialized")
        except Exception as e:
            logfire.error(f"❌ Failed to init Redis Semantic Cache: {e}")
            return None
    return _cache

def check_cache(prompt: str):
    """Checks if a similar question has already been answered."""
    cache = get_semantic_cache()
    if not cache: return None
    
    try:
        results = cache.check(prompt=prompt)
        if results:
            logfire.info(f"✨ Cache Hit! Found similar answer for: {prompt[:50]}...")
            return results[0]["response"]
    except Exception as e:
        logfire.warn(f"⚠️ Cache check failed: {e}")
    return None

def update_cache(prompt: str, response: str):
    """Stores a new answer in the semantic cache."""
    cache = get_semantic_cache()
    if not cache: return
    
    try:
        cache.store(prompt=prompt, response=response)
        logfire.info("💾 Answer saved to Semantic Cache")
    except Exception as e:
        logfire.warn(f"⚠️ Cache storage failed: {e}")
