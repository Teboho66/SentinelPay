"""
SentinelPay – Pattern 6: Singleton
=====================================
Intent  : Ensure a class has only one instance and provide a global point of
          access to it.

Domain use-case
---------------
AuditLogger is the central, append-only audit trail for SentinelPay.  Every
microservice writes to it.  A second instance would split the audit trail and
corrupt compliance reporting — so it must be a Singleton.

Implementation
--------------
Thread safety is achieved via a threading.Lock.  The double-checked locking
idiom is used to avoid acquiring the lock on every read after the instance
is first created.

Why Singleton here?
  - Regulatory compliance requires a single, authoritative audit trail.
  - Keeping a single in-memory log during a request lifetime prevents
    duplicate entries from multiple logger instances.
  - Resource cost: the logger maintains an open write-buffer; opening
    multiple buffers would waste I/O resources.
"""

from __future__ import annotations
import threading
from datetime import datetime
from src.models import AuditLog


class AuditLogger:
    """
    Thread-safe Singleton audit logger.

    Usage
    -----
    logger = AuditLogger.get_instance()
    logger.log("TRANSACTION_APPROVED", actor="system", details={"txn_id": "..."})
    """

    _instance: AuditLogger | None = None
    _lock: threading.Lock = threading.Lock()

    def __init__(self) -> None:
        # Guard: prevent direct construction.
        if AuditLogger._instance is not None:
            raise RuntimeError(
                "AuditLogger is a Singleton. Use AuditLogger.get_instance()."
            )
        self._logs: list[AuditLog] = []
        self._created_at: datetime = datetime.utcnow()

    # ── Singleton accessor ────────────────────────────────────────────────────

    @classmethod
    def get_instance(cls) -> AuditLogger:
        """
        Double-checked locking: fast path skips the lock once the instance
        exists; the slow path acquires the lock only for the first creation.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:       # second check inside lock
                    cls._instance = cls.__new__(cls)
                    cls._instance._logs = []
                    cls._instance._created_at = datetime.utcnow()
        return cls._instance

    # ── Prevent cloning / pickling ────────────────────────────────────────────

    def __copy__(self) -> AuditLogger:
        raise RuntimeError("AuditLogger cannot be copied.")

    def __deepcopy__(self, _memo: dict) -> AuditLogger:
        raise RuntimeError("AuditLogger cannot be deep-copied.")

    # ── Public API ────────────────────────────────────────────────────────────

    def log(self, action: str, actor: str, details: dict | None = None) -> AuditLog:
        """Create and persist an AuditLog entry."""
        entry = AuditLog(action=action, actor=actor, details=details or {})
        with self._lock:
            self._logs.append(entry)
        return entry

    def get_logs(self) -> list[AuditLog]:
        """Return an immutable snapshot of the current audit trail."""
        with self._lock:
            return list(self._logs)

    def filter_by_action(self, action: str) -> list[AuditLog]:
        with self._lock:
            return [log for log in self._logs if log.action == action]

    def clear(self) -> None:
        """
        Clear the log — intended for test teardown only.
        In production, audit logs are never deleted.
        """
        with self._lock:
            self._logs.clear()

    @property
    def entry_count(self) -> int:
        return len(self._logs)

    @property
    def created_at(self) -> datetime:
        return self._created_at

    # ── Test helper: reset Singleton ─────────────────────────────────────────

    @classmethod
    def _reset(cls) -> None:
        """
        Reset the Singleton instance for unit-test isolation.
        Never call this in production code.
        """
        with cls._lock:
            cls._instance = None

    def __repr__(self) -> str:
        return f"AuditLogger(entries={self.entry_count}, created={self._created_at.isoformat()})"