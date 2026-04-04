import os
import json
import hashlib
import redis
from typing import Optional, Dict, Any

# Initialize Redis client
# We use socket_timeout to handle cases where Redis is not available gracefully
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
try:
    redis_client = redis.from_url(redis_url, socket_timeout=1, decode_responses=True)
except Exception as e:
    print(f"Failed to initialize Redis client: {e}")
    redis_client = None

def get_cache(key: str) -> Optional[Dict[str, Any]]:
    """Retrieve a value from the Redis cache."""
    if not redis_client:
        return None
        
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
    except Exception as e:
        print(f"Redis get error for key {key}: {e}")
        
    return None

def set_cache(key: str, value: Dict[str, Any], expiry: int) -> bool:
    """Store a value in the Redis cache with an expiration time in seconds."""
    if not redis_client:
        return False
        
    try:
        serialized_value = json.dumps(value)
        return redis_client.setex(key, expiry, serialized_value)
    except Exception as e:
        print(f"Redis set error for key {key}: {e}")
        return False

def delete_cache(key: str) -> bool:
    """Delete a value from the Redis cache."""
    if not redis_client:
        return False
        
    try:
        return redis_client.delete(key) > 0
    except Exception as e:
        print(f"Redis delete error for key {key}: {e}")
        return False

def generate_query_hash(query: str) -> str:
    """Generate an MD5 hash of the query for use as a cache key."""
    return hashlib.md5(query.lower().strip().encode('utf-8')).hexdigest()
