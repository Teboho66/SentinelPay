"""
SentinelPay – Assignment 11
repositories/inmemory/implementations.py

In-Memory Implementations for all 7 SentinelPay entity repositories.
Each class inherits the HashMap CRUD from InMemoryRepository and implements
only its entity-specific domain query methods.
"""

from __future__ import annotations
import sys, os
_A10 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "Assignment10"))
if _A10 not in sys.path:
    sys.path.insert(0, _A10)

from typing import List, Optional

from src.models import (
    Transaction, FraudCase, MLModel, AuditRecord,
    AccountProfile, CustomerDispute, StepUpChallenge,
    FraudDecision, RiskTier, CaseStatus, CasePriority,
    ModelName, ModelStage, DisputeStatus, ChallengeStatus,
)
from repositories.interfaces import (
    TransactionRepository, FraudCaseRepository, MLModelRepository,
    AuditRecordRepository, AccountProfileRepository,
    CustomerDisputeRepository, StepUpChallengeRepository,
)
from .base_inmemory import InMemoryRepository


# ══════════════════════════════════════════════════════════════════════════════
# InMemoryTransactionRepository
# ══════════════════════════════════════════════════════════════════════════════

class InMemoryTransactionRepository(InMemoryRepository[Transaction], TransactionRepository):
    """
    HashMap-backed Transaction store.
    Primary key: transaction_id
    """
    def _get_id(self, entity: Transaction) -> str:
        return entity.transaction_id


    def find_by_account_id_token(self, account_id_token: str) -> List[Transaction]:
        """FR-05: retrieve all transactions for an account (velocity feature building)."""
        with self._lock:
            return [
                t for t in self._storage.values()
                if t.account_id_token == account_id_token
            ]

    def find_by_decision(self, decision: FraudDecision) -> List[Transaction]:
        """UC11: filter transactions by fraud decision for audit reports."""
        with self._lock:
            return [
                t for t in self._storage.values()
                if t.decision == decision
            ]

    def find_by_risk_tier(self, risk_tier: RiskTier) -> List[Transaction]:
        with self._lock:
            return [
                t for t in self._storage.values()
                if t.risk_tier == risk_tier
            ]

    def find_flagged(self) -> List[Transaction]:
        """FR-09: return all HARD_BLOCK transactions for case generation pipeline."""
        return self.find_by_decision(FraudDecision.HARD_BLOCK)


# ══════════════════════════════════════════════════════════════════════════════
# InMemoryFraudCaseRepository
# ══════════════════════════════════════════════════════════════════════════════

class InMemoryFraudCaseRepository(InMemoryRepository[FraudCase], FraudCaseRepository):
    """
    HashMap-backed FraudCase store.
    Primary key: case_id
    """
    def _get_id(self, entity: FraudCase) -> str:
        return entity.case_id


    def find_by_transaction_id(self, transaction_id: str) -> Optional[FraudCase]:
        """UC7: one FraudCase per Transaction (0..1 composition from A9 diagram)."""
        with self._lock:
            for case in self._storage.values():
                if case.transaction_id == transaction_id:
                    return case
            return None

    def find_by_status(self, status: CaseStatus) -> List[FraudCase]:
        """FR-10: analyst dashboard filters cases by status."""
        with self._lock:
            return [c for c in self._storage.values() if c.status == status]

    def find_by_priority(self, priority: CasePriority) -> List[FraudCase]:
        """FR-09: P1 cases surface at top of analyst queue."""
        with self._lock:
            return [c for c in self._storage.values() if c.priority == priority]

    def find_open_cases(self) -> List[FraudCase]:
        """Return OPEN and IN_REVIEW cases for the analyst working queue."""
        with self._lock:
            return [
                c for c in self._storage.values()
                if c.status in (CaseStatus.OPEN, CaseStatus.IN_REVIEW)
            ]

    def find_by_analyst_id(self, analyst_id: str) -> List[FraudCase]:
        with self._lock:
            return [
                c for c in self._storage.values()
                if c.assigned_analyst_id == analyst_id
            ]


# ══════════════════════════════════════════════════════════════════════════════
# InMemoryMLModelRepository
# ══════════════════════════════════════════════════════════════════════════════

class InMemoryMLModelRepository(InMemoryRepository[MLModel], MLModelRepository):
    """
    HashMap-backed MLModel store.
    Primary key: model_id
    """
    def _get_id(self, entity: MLModel) -> str:
        return entity.model_id


    def find_by_model_name(self, model_name: ModelName) -> List[MLModel]:
        """FR-13: find all versions of a specific model type."""
        with self._lock:
            return [m for m in self._storage.values() if m.model_name == model_name]

    def find_by_stage(self, stage: ModelStage) -> List[MLModel]:
        with self._lock:
            return [m for m in self._storage.values() if m.stage == stage]

    def find_production_models(self) -> List[MLModel]:
        """FR-14: Model Loader polls this every 60 seconds for hot-swap detection."""
        return self.find_by_stage(ModelStage.PRODUCTION)

    def find_by_name_and_stage(
        self, model_name: ModelName, stage: ModelStage
    ) -> Optional[MLModel]:
        with self._lock:
            for m in self._storage.values():
                if m.model_name == model_name and m.stage == stage:
                    return m
            return None


# ══════════════════════════════════════════════════════════════════════════════
# InMemoryAuditRecordRepository
# ══════════════════════════════════════════════════════════════════════════════

class InMemoryAuditRecordRepository(InMemoryRepository[AuditRecord], AuditRecordRepository):
    """
    HashMap-backed AuditRecord store.
    Primary key: audit_id
    AuditRecords are immutable — save() is treated as append-only.
    BR-AR2: delete() raises RuntimeError to mirror the PostgreSQL role restriction.
    """
    def _get_id(self, entity: AuditRecord) -> str:
        return entity.audit_id


    def delete(self, entity_id: str) -> None:
        """
        AuditRecords cannot be deleted (BR-AR2).
        DELETE privilege is revoked in production at the database role level.
        """
        raise RuntimeError(
            "AuditRecord deletion is prohibited (BR-AR2). "
            "Audit records are retained for 7 years per FSCA requirements."
        )

    def find_by_transaction_id(self, transaction_id: str) -> Optional[AuditRecord]:
        """FR-15: 1-to-1 relationship between Transaction and AuditRecord."""
        with self._lock:
            for record in self._storage.values():
                if record.transaction_id == transaction_id:
                    return record
            return None

    def find_by_decision(self, decision: str) -> List[AuditRecord]:
        """UC11: Compliance Officer filters audit report by decision type."""
        with self._lock:
            return [r for r in self._storage.values() if r.decision == decision]

    def find_tampered(self, signing_key: str) -> List[AuditRecord]:
        """
        NFR-S4 daily integrity check: re-verify every record's HMAC hash.
        Returns records where verify_integrity() returns False.
        """
        tampered = []
        with self._lock:
            records = list(self._storage.values())
        for record in records:
            if not record.verify_integrity(signing_key):
                tampered.append(record)
        return tampered


# ══════════════════════════════════════════════════════════════════════════════
# InMemoryAccountProfileRepository
# ══════════════════════════════════════════════════════════════════════════════

class InMemoryAccountProfileRepository(
    InMemoryRepository[AccountProfile], AccountProfileRepository
):
    """
    HashMap-backed AccountProfile store.
    Primary key: account_id_token
    In production this is backed by Redis for sub-millisecond feature lookup.
    """
    def _get_id(self, entity: AccountProfile) -> str:
        return entity.account_id_token


    def find_new_accounts(self) -> List[AccountProfile]:
        """BR-AP1: accounts with < 10 transactions receive population-average baselines."""
        with self._lock:
            return [p for p in self._storage.values() if p.is_new_account]

    def find_by_risk_tier_override(self, tier: RiskTier) -> List[AccountProfile]:
        with self._lock:
            return [
                p for p in self._storage.values()
                if p.risk_tier_override == tier
            ]


# ══════════════════════════════════════════════════════════════════════════════
# InMemoryCustomerDisputeRepository
# ══════════════════════════════════════════════════════════════════════════════

class InMemoryCustomerDisputeRepository(
    InMemoryRepository[CustomerDispute], CustomerDisputeRepository
):
    """
    HashMap-backed CustomerDispute store.
    Primary key: dispute_id
    """
    def _get_id(self, entity: CustomerDispute) -> str:
        return entity.dispute_id


    def find_by_transaction_id(self, transaction_id: str) -> Optional[CustomerDispute]:
        """
        BR-CD2: one dispute per transaction.
        Returns None when no dispute exists for this transaction_id.
        """
        with self._lock:
            for d in self._storage.values():
                if d.transaction_id == transaction_id:
                    return d
            return None

    def find_by_status(self, status: DisputeStatus) -> List[CustomerDispute]:
        with self._lock:
            return [d for d in self._storage.values() if d.status == status]

    def find_open_disputes(self) -> List[CustomerDispute]:
        """Analyst dashboard: all disputes requiring action."""
        with self._lock:
            return [
                d for d in self._storage.values()
                if d.status in (DisputeStatus.OPEN, DisputeStatus.UNDER_REVIEW)
            ]

    def find_by_customer_id_token(self, customer_id_token: str) -> List[CustomerDispute]:
        with self._lock:
            return [
                d for d in self._storage.values()
                if d._customer_id_token == customer_id_token
            ]


# ══════════════════════════════════════════════════════════════════════════════
# InMemoryStepUpChallengeRepository
# ══════════════════════════════════════════════════════════════════════════════

class InMemoryStepUpChallengeRepository(
    InMemoryRepository[StepUpChallenge], StepUpChallengeRepository
):
    """
    HashMap-backed StepUpChallenge store.
    Primary key: challenge_id
    """
    def _get_id(self, entity: StepUpChallenge) -> str:
        return entity.challenge_id


    def find_by_transaction_id(self, transaction_id: str) -> Optional[StepUpChallenge]:
        """FR-08: Step-Up Auth API looks up the active OTP challenge by transaction."""
        with self._lock:
            for c in self._storage.values():
                if c.transaction_id == transaction_id:
                    return c
            return None

    def find_by_status(self, status: ChallengeStatus) -> List[StepUpChallenge]:
        with self._lock:
            return [c for c in self._storage.values() if c.status == status]

    def find_expired(self) -> List[StepUpChallenge]:
        """
        Cleanup job: find challenges whose TTL has elapsed but are still
        GENERATED or DELIVERED (not yet marked EXPIRED or escalated).
        """
        with self._lock:
            return [
                c for c in self._storage.values()
                if c.status in (ChallengeStatus.GENERATED, ChallengeStatus.DELIVERED)
                and c.is_expired()
            ]