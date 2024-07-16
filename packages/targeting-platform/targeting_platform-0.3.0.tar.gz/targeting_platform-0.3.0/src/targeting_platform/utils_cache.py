"""Operations with cache module."""

import hashlib
import json
from typing import Any, Optional

import logging
from redis import Redis, ConnectionPool
from redis.backoff import ExponentialBackoff
from redis.exceptions import BusyLoadingError, ConnectionError, TimeoutError
from redis.retry import Retry


def serialize(obj: Any) -> Any:
    """Serialize object to preserve tuples.

    Args:
    ----
        obj (Any): object to serialize

    Returns:
    -------
        Any: serialized object

    """
    if isinstance(obj, tuple):
        return {"__tuple__": True, "items": serialize(list(obj))}
    elif isinstance(obj, list):
        return [serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: serialize(value) for key, value in obj.items()}
    else:
        return obj


def deserialize(obj: Any) -> Any:
    """Deerialize object to preserve tuples.

    Args:
    ----
        obj (Any): object to deserialize

    Returns:
    -------
        Any: deserialized object

    """
    if isinstance(obj, list):
        return [deserialize(item) for item in obj]
    elif isinstance(obj, dict):
        if "__tuple__" in obj:
            return tuple(deserialize(obj["items"]))
        else:
            return {key: deserialize(value) for key, value in obj.items()}
    else:
        return obj


class RedisCache:
    """Cache based on Redis."""

    CACHE_KEYS_PREFIX = "PLATFORM_CACHE_"
    LOCK_KEYS_PREFIX = "PLATFORM_LOCK_"

    def __init__(self, redis_host: str = "localhost:6379") -> None:
        """Create cache class.

        Args:
        ----
            redis_host (str, optional): redis host for read/write. Defaults to "localhost:6379".

        """
        self._redis_client = Redis(
            connection_pool=ConnectionPool.from_url(
                url=f"redis://{redis_host}?decode_responses=True",
                retry=Retry(ExponentialBackoff(), 3),
                retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError],
            )
        )

    def _get_key_name(self, name: str, *args: Optional[Any], **kwargs: Optional[Any]) -> str:
        """Get nmae for cache.

        Args:
        ----
            name (str): function name.
            args (Optional[Any]): arbitrary parameters.
            kwargs (Optional[Any]): arbitrary parameters.

        Returns:
        -------
            str: cache key.

        """
        # prefix if only allowed changeble parameter
        key_params = (
            args,
            tuple(sorted([(k, v) for k, v in kwargs.items() if k != "prefix"])),
        )
        return f"{name}_{hashlib.md5(bytearray(str(key_params),'utf-8')).hexdigest()}"

    def get_cache(self, name: str, *args: Optional[Any], **kwargs: Optional[Any]) -> Any:
        """Get value from cache.

        Args:
        ----
            name (str): name of cache instance.
            args (Optional[Any]): arbitrary parameters.
            kwargs (Optional[Any]): arbitrary parameters.

        Returns:
        -------
            Any: cached value.

        """
        key = self._get_key_name(name=f"{self.CACHE_KEYS_PREFIX}{name}", args=args, kwargs=kwargs)

        try:
            cached_value = self._redis_client.get(key)
            value = deserialize(json.loads(cached_value)["cache"]) if cached_value else None
        except Exception:
            value = None

        if value:
            logging.info(f"CACHE: Use cached data for {key}")

        return value

    def set_cache(self, name: str, value: Any, ttl: int = 3600, *args: Optional[Any], **kwargs: Optional[Any]) -> None:
        """Set cache value.

        Args:
        ----
            name (str): name of cache instance.
            value (Any): value.
            ttl (int, optional): TTL. Defaults to 3600.
            args (Optional[Any]): arbitrary parameters
            kwargs (Optional[Any]): arbitrary parameters

        """
        key = self._get_key_name(name=f"{self.CACHE_KEYS_PREFIX}{name}", args=args, kwargs=kwargs)

        self._redis_client.set(key, json.dumps({"cache": serialize(value)}))
        self._redis_client.expire(key, ttl)
        logging.info(f"CACHE: Set cached data for {key}")

    def delete_cache(self, name: str, *args: Optional[Any], **kwargs: Optional[Any]) -> None:
        """Delete cache value.

        Args:
        ----
            name (str): name of cache instance.
            args (Optional[Any]): arbitrary parameters.
            kwargs (Optional[Any]): arbitrary parameters.

        """
        key = self._get_key_name(name=f"{self.CACHE_KEYS_PREFIX}{name}", args=args, kwargs=kwargs)

        logging.info(f"CACHE: Search for {key}")
        keys = self._redis_client.keys(key)
        if keys:
            self._redis_client.delete(*keys)
            logging.info(f"CACHE: Delete cached data for {key}")

    def lock(self, name: str, *args: Optional[Any], **kwargs: Optional[Any]) -> bool:
        """Acquire lock for operation on parameters.

        Args:
        ----
            name (str): name of function to call lock.
            args (Optional[Any]): arbitrary parameters
            kwargs (Optional[Any]): arbitrary parameters

        Returns:
        -------
            bool: true if lock was acquired.

        """
        key = self._get_key_name(name=self.LOCK_KEYS_PREFIX, args=args, kwargs=kwargs)

        result = self._redis_client.setnx(key, name)
        if result:
            self._redis_client.expire(key, 3600)
            logging.info(f"LOCK: Acquired lock for {key} by {name}")

        return result

    def release_lock(self, *args: Optional[Any], **kwargs: Optional[Any]) -> None:
        """Set cache value.

        Args:
        ----
            args (Optional[Any]): arbitrary parameters
            kwargs (Optional[Any]): arbitrary parameters

        """
        key = self._get_key_name(name=self.LOCK_KEYS_PREFIX, args=args, kwargs=kwargs)

        self._redis_client.delete(key)
        logging.info(f"LOCK: Release lock for {key}")
