"""
SentinelPay – Assignment 11
repositories/inmemory/base_inmemory.py

In-Memory Base Repository
===========================
Provides the HashMap (dict) storage and the five generic CRUD methods
shared across all seven in-memory implementations. Entity-specific
repositories sub-class this and only need to implement their domain-specific
query methods — no boilerplate duplication.

Storage: Python dict keyed by the entity's string ID.
Thread safety: threading.Lock guards every read and write so the in-memory
store is safe under the concurrent Kafka consumer threads SentinelPay runs.
"""

from __future__ import annotations
import threading
from typing import Generic, List, Optional, TypeVar

from repositories.base import Repository

T = TypeVar("T")


class InMemoryRepository(Repository[T, str]):
    """
    Concrete generic base using a dict as the backing store.
    Sub-classes inherit all five CRUD methods and only implement
    their entity-specific query methods.
    """

    def __init__(self) -> None:
        self._storage: dict[str, T] = {}
        self._lock: threading.Lock = threading.Lock()

    # ── Generic CRUD (all sub-classes inherit these) ──────────────────────────

    def save(self, entity: T) -> None:
        """Upsert: insert if new, replace if ID already exists."""
        entity_id = self._get_id(entity)
        with self._lock:
            self._storage[entity_id] = entity

    def find_by_id(self, entity_id: str) -> Optional[T]:
        with self._lock:
            return self._storage.get(entity_id)

    def find_all(self) -> List[T]:
        """Return a snapshot list — mutations do not affect the store."""
        with self._lock:
            return list(self._storage.values())

    def delete(self, entity_id: str) -> None:
        """Idempotent — no error raised if ID does not exist."""
        with self._lock:
            self._storage.pop(entity_id, None)

    def count(self) -> int:
        with self._lock:
            return len(self._storage)

    def exists(self, entity_id: str) -> bool:
        with self._lock:
            return entity_id in self._storage

    def clear(self) -> None:
        """Remove all entries. Used for test teardown."""
        with self._lock:
            self._storage.clear()

    # ── ID extraction hook ────────────────────────────────────────────────────

    def _get_id(self, entity: T) -> str:
        """
        Extracts the primary key from an entity.
        Sub-classes override this when the ID property name differs from 'id'.
        """
        # Try common ID property names used across the SentinelPay domain
        for attr in ("transaction_id", "case_id", "model_id", "audit_id",
                     "account_id_token", "dispute_id", "challenge_id", "id"):
            val = getattr(entity, attr, None)
            if val is not None:
                return str(val)
        raise AttributeError(
            f"Cannot determine ID for entity of type {type(entity).__name__}. "
            f"Override _get_id() in the sub-class."
        )