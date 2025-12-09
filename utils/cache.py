"""
Thread-safe caching utilities for the pizzeria application.
"""
import threading
import time
from typing import Any, Dict, Optional, Callable
from functools import wraps
from logging_config import get_logger

logger = get_logger("pizzeria.cache")


class ThreadSafeCache:
    """
    Thread-safe cache with TTL (Time To Live) support.
    
    Features:
    - Thread-safe get/set operations
    - TTL support for automatic expiration
    - Size limit with LRU eviction
    - Statistics tracking
    """
    
    def __init__(self, max_size: int = 100, default_ttl: Optional[float] = None):
        """
        Initialize thread-safe cache.
        
        Args:
            max_size: Maximum number of items in cache (0 = unlimited)
            default_ttl: Default time-to-live in seconds (None = no expiration)
        """
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._lock = threading.RLock()  # Reentrant lock for nested calls
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
        self._evictions = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            value, expiry = self._cache[key]
            
            # Check if expired
            if expiry is not None and time.time() > expiry:
                del self._cache[key]
                self._misses += 1
                return None
            
            self._hits += 1
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = use default_ttl, 0 = no expiration)
        """
        with self._lock:
            # Calculate expiry time
            if ttl is None:
                ttl = self._default_ttl
            
            expiry = None
            if ttl is not None and ttl > 0:
                expiry = time.time() + ttl
            
            # Check size limit
            if self._max_size > 0 and key not in self._cache:
                if len(self._cache) >= self._max_size:
                    # Evict oldest item (simple FIFO)
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
                    self._evictions += 1
            
            self._cache[key] = (value, expiry)
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            now = time.time()
            expired_keys = [
                key for key, (_, expiry) in self._cache.items()
                if expiry is not None and now > expiry
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0.0
            
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.2f}%",
                "evictions": self._evictions
            }
    
    def __len__(self) -> int:
        """Get number of items in cache."""
        with self._lock:
            return len(self._cache)
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache (and is not expired)."""
        return self.get(key) is not None


def cached(ttl: Optional[float] = None, max_size: int = 100, cache_key: Optional[Callable] = None):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time-to-live in seconds (None = no expiration)
        max_size: Maximum cache size
        cache_key: Optional function to generate cache key from arguments
    
    Example:
        @cached(ttl=300)  # Cache for 5 minutes
        def expensive_operation(arg1, arg2):
            return slow_computation(arg1, arg2)
    """
    cache = ThreadSafeCache(max_size=max_size, default_ttl=ttl)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key:
                key = cache_key(*args, **kwargs)
            else:
                # Default: use function name + args + kwargs
                key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Compute result
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(key, result)
            
            return result
        
        # Attach cache to function for manual control
        wrapper.cache = cache
        return wrapper
    
    return decorator

