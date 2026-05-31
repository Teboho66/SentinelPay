"""
SentinelPay – Assignment 11
stubs/filesystem_repository.py

FileSystem JSON Repository Stub
=================================
Demonstrates how the repository layer is future-proofed for a JSON/filesystem
backend. This is a partial implementation — the pattern is fully shown for
save() and find_by_id(); remaining CRUD methods follow the same structure.

When to use:
  - Local development / testing without a running database
  - Audit log archival to flat files for long-term retention (BR-AR3: 7 years)
  - Exporting fraud case reports as JSON for regulatory submission

Design notes:
  - All entities are serialised to JSON using their to_kafka_payload() /
    to_compliance_report() methods where available, or __dict__ fallback.
  - The file path is injected at construction time — the repository is
    completely storage-location-agnostic.
  - Thread safety: file writes use a threading.Lock to prevent concurrent
    write corruption.
"""

from __future__ import annotations
import json
import os
import threading
from typing import List, Optional


class FileSystemRepositoryStub:
    """
    Stub: JSON file-backed repository.
    Implements the Repository interface partially to show the pattern.
    A full implementation would serialise/deserialise each domain entity
    to/from JSON using entity-specific serialisers.
    """

    def __init__(self, entity_name: str, base_dir: str = "/tmp/sentinelpay") -> None:
        self._entity_name = entity_name
        self._file_path = os.path.join(base_dir, f"{entity_name}.json")
        self._lock = threading.Lock()
        os.makedirs(base_dir, exist_ok=True)
        if not os.path.exists(self._file_path):
            with open(self._file_path, "w") as f:
                json.dump({}, f)

    # ── CRUD stubs (pattern shown — full deserialisation requires entity-specific mappers) ──

    def save(self, entity: object) -> None:
        """
        Serialise entity to JSON and persist to file.
        Uses to_kafka_payload() where available (Transaction), or
        to_compliance_report() (AuditRecord), or __dict__ fallback.
        """
        entity_id = self._extract_id(entity)
        payload = self._serialise(entity)
        with self._lock:
            data = self._load_all()
            data[entity_id] = payload
            self._write_all(data)

    def find_by_id(self, entity_id: str) -> Optional[dict]:
        """
        Returns the raw JSON dict for the entity.
        A full implementation would deserialise back to the domain object.
        """
        data = self._load_all()
        return data.get(entity_id)

    def find_all(self) -> List[dict]:
        return list(self._load_all().values())

    def delete(self, entity_id: str) -> None:
        with self._lock:
            data = self._load_all()
            data.pop(entity_id, None)
            self._write_all(data)

    def count(self) -> int:
        return len(self._load_all())

    def exists(self, entity_id: str) -> bool:
        return entity_id in self._load_all()

    # ── Private helpers ───────────────────────────────────────────────────────

    def _load_all(self) -> dict:
        with open(self._file_path, "r") as f:
            return json.load(f)

    def _write_all(self, data: dict) -> None:
        with open(self._file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _serialise(self, entity: object) -> dict:
        """Try entity-specific serialisers, fall back to __dict__."""
        for method in ("to_kafka_payload", "to_compliance_report"):
            if hasattr(entity, method):
                return getattr(entity, method)()
        # Generic fallback — strips private underscore attributes
        return {
            k.lstrip("_"): str(v)
            for k, v in vars(entity).items()
        }

    def _extract_id(self, entity: object) -> str:
        for attr in ("transaction_id", "case_id", "model_id", "audit_id",
                     "account_id_token", "dispute_id", "challenge_id"):
            val = getattr(entity, attr, None)
            if val is not None:
                return str(val)
        raise AttributeError(f"Cannot determine ID for {type(entity).__name__}")

    def __repr__(self) -> str:
        return f"FileSystemRepositoryStub(entity={self._entity_name}, path={self._file_path})"