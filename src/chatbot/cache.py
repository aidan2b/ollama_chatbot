"""Caching module for LLM instances and responses."""

from __future__ import annotations

import logging
from typing import Any

import cachetools
from cachetools import TTLCache

from chatbot.settings import settings

logger = logging.getLogger(__name__)


class LLMCache:
    """Cache for LLM instances and responses."""

    def __init__(self) -> None:
        """Initialize the cache with configured size and TTL."""
        self._llm_cache: TTLCache[str, Any] = TTLCache(
            maxsize=settings.cache.size,
            ttl=settings.cache.ttl,
        )
        self._response_cache: TTLCache[str, str] = TTLCache(
            maxsize=settings.cache.size,
            ttl=settings.cache.ttl,
        )

    def get_llm(self, model_name: str) -> Any | None:
        """Get cached LLM instance for a model.

        Args:
            model_name: Name of the model.

        Returns:
            Cached LLM instance or None if not found.
        """
        return self._llm_cache.get(model_name)

    def set_llm(self, model_name: str, llm_instance: Any) -> None:
        """Cache an LLM instance.

        Args:
            model_name: Name of the model.
            llm_instance: LLM instance to cache.
        """
        self._llm_cache[model_name] = llm_instance
        logger.debug("Cached LLM instance for model: %s", model_name)

    def get_response(self, cache_key: str) -> str | None:
        """Get cached response.

        Args:
            cache_key: Key for the cached response.

        Returns:
            Cached response or None if not found.
        """
        return self._response_cache.get(cache_key)

    def set_response(self, cache_key: str, response: str) -> None:
        """Cache a response.

        Args:
            cache_key: Key for caching the response.
            response: Response to cache.
        """
        self._response_cache[cache_key] = response
        logger.debug("Cached response with key: %s", cache_key)

    def clear(self) -> None:
        """Clear all caches."""
        self._llm_cache.clear()
        self._response_cache.clear()
        logger.info("Cleared all caches")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics.
        """
        return {
            "llm_cache": {
                "size": self._llm_cache.currsize,
                "max_size": self._llm_cache.maxsize,
                "hit_rate": self._llm_cache.hit_rate
                if hasattr(self._llm_cache, "hit_rate")
                else "N/A",
            },
            "response_cache": {
                "size": self._response_cache.currsize,
                "max_size": self._response_cache.maxsize,
                "hit_rate": self._response_cache.hit_rate
                if hasattr(self._response_cache, "hit_rate")
                else "N/A",
            },
        }


# Global cache instance
cache = LLMCache()


if __name__ == "__main__":
    # Test the cache
    print("Testing cache...")
    cache.set_llm("test-model", "test-instance")
    print("LLM cache test:", cache.get_llm("test-model"))

    cache.set_response("test-key", "test-response")
    print("Response cache test:", cache.get_response("test-key"))

    print("Cache stats:", cache.get_cache_stats())
    cache.clear()
    print("Cache cleared")
