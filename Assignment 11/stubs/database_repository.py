"""
SentinelPay – Assignment 11
stubs/database_repository.py

Database Repository Stub
==========================
Demonstrates how the repository layer extends to a real database backend
(PostgreSQL for relational entities, MongoDB for document-style storage).

This stub shows the interface contract and the connection setup pattern.
The actual SQL/NoSQL query implementations are left as placeholders —
a full implementation would use SQLAlchemy (PostgreSQL) or PyMongo (MongoDB).

SentinelPay database mapping (from A3 ARCHITECTURE.md):
  Transaction       → PostgreSQL fraud_decisions table
  FraudCase         → PostgreSQL fraud_cases table
  AuditRecord       → PostgreSQL audit_records table (append-only, partitioned)
  MLModel           → MLflow model registry (PostgreSQL backend)
  AccountProfile    → Redis (primary) + Cassandra (30-day baseline)
  CustomerDispute   → PostgreSQL disputes table
  StepUpChallenge   → Redis with TTL enforcement
"""

from __future__ import annotations
from typing import List, Optional


class DatabaseRepositoryStub:
    """
    Stub: database-backed repository.
    Shows the connection setup and query patterns without requiring a
    live database connection in the academic environment.

    A full implementation would:
      1. Accept a SQLAlchemy engine or PyMongo client at construction.
      2. Map each domain entity to its database schema.
      3. Implement each CRUD method using parameterised queries.
      4. Use connection pooling for the high-throughput SentinelPay pipeline.
    """

    def __init__(self, entity_name: str, connection_string: str = "STUB") -> None:
        self._entity_name = entity_name
        self._connection_string = connection_string
        # In production: self._engine = create_engine(connection_string)
        print(
            f"[DatabaseRepositoryStub] Would connect to: {connection_string} "
            f"for entity: {entity_name}"
        )

    # ── CRUD stubs ────────────────────────────────────────────────────────────

    def save(self, entity: object) -> None:
        """
        PostgreSQL: INSERT ... ON CONFLICT (id) DO UPDATE (upsert).
        MongoDB: db.collection.replace_one({"_id": id}, document, upsert=True)
        """
        raise NotImplementedError(
            "DatabaseRepository.save() requires a live database connection. "
            "Use storage_type='MEMORY' for tests or 'FILESYSTEM' for local dev."
        )

    def find_by_id(self, entity_id: str) -> Optional[object]:
        """
        PostgreSQL: SELECT * FROM {table} WHERE id = %s
        MongoDB: db.collection.find_one({"_id": entity_id})
        """
        raise NotImplementedError("Database backend not yet implemented.")

    def find_all(self) -> List[object]:
        """
        PostgreSQL: SELECT * FROM {table}
        MongoDB: db.collection.find({})
        """
        raise NotImplementedError("Database backend not yet implemented.")

    def delete(self, entity_id: str) -> None:
        """
        PostgreSQL: DELETE FROM {table} WHERE id = %s
        Note: AuditRecord.delete() raises RuntimeError regardless of backend (BR-AR2).
        """
        raise NotImplementedError("Database backend not yet implemented.")

    def count(self) -> int:
        """PostgreSQL: SELECT COUNT(*) FROM {table}"""
        raise NotImplementedError("Database backend not yet implemented.")

    def exists(self, entity_id: str) -> bool:
        """PostgreSQL: SELECT 1 FROM {table} WHERE id = %s LIMIT 1"""
        raise NotImplementedError("Database backend not yet implemented.")

    def __repr__(self) -> str:
        return (
            f"DatabaseRepositoryStub(entity={self._entity_name}, "
            f"connection={'configured' if self._connection_string != 'STUB' else 'stub'})"
        )