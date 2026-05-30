"""
SentinelPay – Assignment 11
factories/repository_factory.py

Repository Factory
===================
Implements the Factory Pattern to decouple service classes from specific
storage backends. Services request a repository by entity name and storage
type; the factory resolves and returns the correct implementation.

Why Factory over Dependency Injection here?
-------------------------------------------
SentinelPay already uses DI at the microservice level (Spring Boot's
@Autowired / FastAPI's Depends). At the repository level, a Factory is a
better fit because:

1. Storage backend can change per-environment (MEMORY in tests, DATABASE in
   production) without changing the service classes that consume the repositories.
2. A single `RepositoryFactory.get("Transaction", "MEMORY")` call in a
   service's __init__ is more explicit than a multi-layer DI container setup
   in a Python-only academic project.
3. The Factory sits naturally next to the creational patterns already built
   in Assignment 10 — adding a new backend (e.g., "REDIS", "MONGODB") requires
   only one new branch in get(), not a new DI binding file.

Supported storage types
-----------------------
  "MEMORY"     → In-memory HashMap (current full implementation)
  "FILESYSTEM" → JSON file-based store (stub — future implementation)
  "DATABASE"   → PostgreSQL/MongoDB (stub — future implementation)
"""

from __future__ import annotations
import sys
import os

_A11 = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _A11 not in sys.path:
    sys.path.insert(0, _A11)

from repositories.interfaces import (
    TransactionRepository, FraudCaseRepository, MLModelRepository,
    AuditRecordRepository, AccountProfileRepository,
    CustomerDisputeRepository, StepUpChallengeRepository,
)
from repositories.inmemory import (
    InMemoryTransactionRepository, InMemoryFraudCaseRepository,
    InMemoryMLModelRepository, InMemoryAuditRecordRepository,
    InMemoryAccountProfileRepository, InMemoryCustomerDisputeRepository,
    InMemoryStepUpChallengeRepository,
)


# ── Registry types ────────────────────────────────────────────────────────────

_ENTITY_NAMES = {
    "transaction", "fraudcase", "mlmodel", "auditrecord",
    "accountprofile", "customerdispute", "stepupchallenge",
}

_STORAGE_TYPES = {"MEMORY", "FILESYSTEM", "DATABASE"}


class RepositoryFactory:
    """
    Factory that returns the correct repository implementation for a given
    entity and storage backend.

    Usage
    -----
    repo = RepositoryFactory.get("Transaction", "MEMORY")
    repo.save(transaction)
    """

    # ── In-memory constructors ────────────────────────────────────────────────

    _MEMORY_MAP: dict[str, type] = {
        "transaction":       InMemoryTransactionRepository,
        "fraudcase":         InMemoryFraudCaseRepository,
        "mlmodel":           InMemoryMLModelRepository,
        "auditrecord":       InMemoryAuditRecordRepository,
        "accountprofile":    InMemoryAccountProfileRepository,
        "customerdispute":   InMemoryCustomerDisputeRepository,
        "stepupchallenge":   InMemoryStepUpChallengeRepository,
    }

    @staticmethod
    def get(entity: str, storage_type: str = "MEMORY") -> object:
        """
        Return a repository instance for the requested entity and storage backend.

        Parameters
        ----------
        entity       : Case-insensitive entity name. One of:
                       "Transaction", "FraudCase", "MLModel", "AuditRecord",
                       "AccountProfile", "CustomerDispute", "StepUpChallenge"
        storage_type : "MEMORY" | "FILESYSTEM" | "DATABASE"

        Raises
        ------
        ValueError : Unknown entity name or storage type.
        NotImplementedError : Storage type registered but not yet implemented.
        """
        entity_key = entity.lower().replace("_", "").replace(" ", "")
        storage_key = storage_type.upper()

        if entity_key not in RepositoryFactory._MEMORY_MAP:
            raise ValueError(
                f"Unknown entity '{entity}'. "
                f"Supported: {sorted(RepositoryFactory._MEMORY_MAP)}"
            )

        if storage_key == "MEMORY":
            cls = RepositoryFactory._MEMORY_MAP[entity_key]
            return cls()

        if storage_key == "FILESYSTEM":
            # Stub — see stubs/filesystem_repository.py
            from stubs.filesystem_repository import FileSystemRepositoryStub
            return FileSystemRepositoryStub(entity_key)

        if storage_key == "DATABASE":
            # Stub — see stubs/database_repository.py
            from stubs.database_repository import DatabaseRepositoryStub
            return DatabaseRepositoryStub(entity_key)

        raise ValueError(
            f"Unknown storage type '{storage_type}'. "
            f"Supported: MEMORY, FILESYSTEM, DATABASE"
        )

    @staticmethod
    def get_transaction_repo(storage_type: str = "MEMORY") -> TransactionRepository:
        return RepositoryFactory.get("Transaction", storage_type)

    @staticmethod
    def get_fraud_case_repo(storage_type: str = "MEMORY") -> FraudCaseRepository:
        return RepositoryFactory.get("FraudCase", storage_type)

    @staticmethod
    def get_ml_model_repo(storage_type: str = "MEMORY") -> MLModelRepository:
        return RepositoryFactory.get("MLModel", storage_type)

    @staticmethod
    def get_audit_record_repo(storage_type: str = "MEMORY") -> AuditRecordRepository:
        return RepositoryFactory.get("AuditRecord", storage_type)

    @staticmethod
    def get_account_profile_repo(storage_type: str = "MEMORY") -> AccountProfileRepository:
        return RepositoryFactory.get("AccountProfile", storage_type)

    @staticmethod
    def get_customer_dispute_repo(storage_type: str = "MEMORY") -> CustomerDisputeRepository:
        return RepositoryFactory.get("CustomerDispute", storage_type)

    @staticmethod
    def get_step_up_challenge_repo(storage_type: str = "MEMORY") -> StepUpChallengeRepository:
        return RepositoryFactory.get("StepUpChallenge", storage_type)
