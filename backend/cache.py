import hashlib
from typing import Any, Optional

_memory_cache = {}

def generate_query_hash(query: str) -> str:
    return hashlib.md5(query.lower().strip().encode()).hexdigest()

def get_cache(key: str) -> Optional[Any]:
    return _memory_cache.get(key)

def set_cache(key: str, value: Any, expiry: int = 3600) -> None:
    _memory_cache[key] = value
