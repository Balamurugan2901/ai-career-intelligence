import hashlib
import json
import time
from typing import Dict, Any, Optional, List
from backend.utils.logger import logger


class PipelineCache:
    """
    In-Memory Caching Subsystem for Career Analysis Pipeline.
    Prevents redundant RAG queries and LLM invocations when candidate profiles and target roles remain unchanged.
    """

    def __init__(self, default_ttl_seconds: int = 3600):
        self._store: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl_seconds

    def generate_key(
        self,
        candidate_id: int,
        target_role: str,
        profile_summary: str = "",
        skills: Optional[List[str]] = None,
    ) -> str:
        """Generates a deterministic SHA256 cache key based on candidate parameters."""
        skills_str = json.dumps(sorted(skills or []))
        raw_key = f"{candidate_id}:{target_role.strip().lower()}:{profile_summary}:{skills_str}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached entry if key exists and has not expired."""
        if key not in self._store:
            return None

        entry = self._store[key]
        if entry["expires_at"] and time.time() > entry["expires_at"]:
            logger.info(f"PipelineCache key '{key[:12]}...' has expired. Purging from cache.")
            del self._store[key]
            return None

        logger.info(f"PipelineCache HIT for key '{key[:12]}...'")
        return entry["data"]

    def set(self, key: str, data: Dict[str, Any], ttl_seconds: Optional[int] = None):
        """Stores data payload in cache with TTL."""
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expires_at = time.time() + ttl if ttl > 0 else None
        self._store[key] = {
            "data": data,
            "expires_at": expires_at,
        }
        logger.info(f"PipelineCache SET for key '{key[:12]}...' (TTL: {ttl}s)")

    def invalidate(self, candidate_id: int):
        """Invalidates all cached pipeline entries for a candidate."""
        keys_to_del = [k for k in self._store if k.startswith(f"{candidate_id}:")]
        for k in keys_to_del:
            del self._store[k]
        if keys_to_del:
            logger.info(f"PipelineCache invalidated {len(keys_to_del)} entries for Candidate #{candidate_id}.")

    def clear(self):
        """Clears all cached entries."""
        self._store.clear()
        logger.info("PipelineCache completely cleared.")


# Singleton cache instance
pipeline_cache = PipelineCache()
