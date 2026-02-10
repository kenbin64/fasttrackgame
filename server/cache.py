"""
Redis Caching Layer for ButterflyFx Server

Provides 10-100x performance boost for repeated substrate invocations.
"""

import redis
import json
import hashlib
from typing import Optional, Any
from server.config import settings


class RedisCache:
    """Redis cache manager."""
    
    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            print(f"✅ Redis cache connected: {settings.REDIS_URL}")
        except Exception as e:
            print(f"⚠️  Redis cache unavailable: {e}")
            print(f"   Continuing without cache (performance will be reduced)")
            self.redis_client = None
            self.enabled = False
    
    def _make_key(self, prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments."""
        # Create deterministic hash of arguments
        key_data = json.dumps(args, sort_keys=True)
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16]
        return f"butterflyfx:{prefix}:{key_hash}"
    
    def get(self, prefix: str, *args) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled:
            return None
        
        try:
            key = self._make_key(prefix, *args)
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, prefix: str, value: Any, ttl: Optional[int] = None, *args) -> bool:
        """Set value in cache with optional TTL."""
        if not self.enabled:
            return False
        
        try:
            key = self._make_key(prefix, *args)
            value_json = json.dumps(value)
            
            if ttl is None:
                ttl = settings.REDIS_CACHE_TTL
            
            self.redis_client.setex(key, ttl, value_json)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, prefix: str, *args) -> bool:
        """Delete value from cache."""
        if not self.enabled:
            return False
        
        try:
            key = self._make_key(prefix, *args)
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(f"butterflyfx:{pattern}:*")
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear error: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        if not self.enabled:
            return {
                "enabled": False,
                "status": "unavailable"
            }
        
        try:
            info = self.redis_client.info()
            return {
                "enabled": True,
                "status": "connected",
                "used_memory_mb": info.get("used_memory", 0) / 1024 / 1024,
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }
        except Exception as e:
            return {
                "enabled": False,
                "status": "error",
                "error": str(e)
            }
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage."""
        total = hits + misses
        if total == 0:
            return 0.0
        return (hits / total) * 100


# Global cache instance
cache = RedisCache()


