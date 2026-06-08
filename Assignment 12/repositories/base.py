"""
SentinelPay – Assignment 11
repositories/base.py

Generic Repository Interface
==============================
Defines the base Repository[T, ID] contract that every entity-specific
repository must satisfy. Using Python's Generic typing avoids code duplication
across the seven SentinelPay entity repositories while keeping the interface
strongly typed.

Design decisions
----------------
- Abstract Base Class (ABC) enforces the contract at the class level rather
  than at runtime, so missing method implementations are caught immediately
  on class definition rather than at first call.
- save() handles both Create and Update — an entity with an ID that already
  exists in the store is overwritten, following the upsert semantics common
  in repository patterns.
- find_by_id() returns Optional[T] rather than raising KeyError; the caller
  decides how to handle a missing entity.
- find_all() returns a list snapshot — mutations to the returned list do not
  affect the underlying store.
- delete() is a no-op when the ID does not exist (idempotent) — callers do
  not need to check existence before deleting.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class Repository(ABC, Generic[T, ID]):
    """
    Generic repository interface.
    All SentinelPay entity repositories extend this interface.
    """

    @abstractmethod
    def save(self, entity: T) -> None:
        """
        Persist an entity (Create or Update / upsert semantics).
        If an entity with the same ID already exists, it is replaced.
        """
        ...

    @abstractmethod
    def find_by_id(self, entity_id: ID) -> Optional[T]:
        """
        Retrieve a single entity by its primary key.
        Returns None when no entity with that ID exists.
        """
        ...

    @abstractmethod
    def find_all(self) -> List[T]:
        """
        Return a snapshot list of all persisted entities.
        The returned list is a copy — mutations do not affect the store.
        """
        ...

    @abstractmethod
    def delete(self, entity_id: ID) -> None:
        """
        Remove the entity with the given ID.
        Idempotent — no error raised if the ID does not exist.
        """
        ...

    @abstractmethod
    def count(self) -> int:
        """Return the total number of stored entities."""
        ...

    @abstractmethod
    def exists(self, entity_id: ID) -> bool:
        """Return True if an entity with this ID is currently stored."""
        ...
