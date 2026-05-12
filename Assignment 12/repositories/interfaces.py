"""
SentinelPay – Assignment 11
repositories/interfaces.py

Entity-Specific Repository Interfaces
========================================
Each interface extends the generic Repository[T, str] with domain-specific
query methods derived from the SentinelPay use cases and functional requirements.

Every query method maps to at least one use case or FR from prior assignments:
  - TransactionRepository  → UC1, UC3, UC4  / FR-01, FR-07
  - FraudCaseRepository    → UC8            / FR-09, FR-10
  - MLModelRepository      → UC10           / FR-13, FR-14
  - AuditRecordRepository  → UC11           / FR-15
  - AccountProfileRepository → UC3          / FR-05
  - CustomerDisputeRepository → UC7         / FR-12
  - StepUpChallengeRepository → UC5         / FR-08
"""

from __future__ import annotations
from abc import abstractmethod
from typing import List, Optional

from .base import Repository

# ── Import domain entities from Assignment 10 ────────────────────────────────
import sys, os
_A10 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Assignment10"))
if _A10 not in sys.path:
    sys.path.insert(0, _A10)

from services.models import (
    Transaction, FraudCase, MLModel, AuditRecord,
    AccountProfile, CustomerDispute, StepUpChallenge,
    FraudDecision, RiskTier, CaseStatus, CasePriority,
    ModelName, ModelStage, DisputeStatus, ChallengeStatus,
)


# ══════════════════════════════════════════════════════════════════════════════
# TransactionRepository
# ══════════════════════════════════════════════════════════════════════════════

class TransactionRepository(Repository[Transaction, str]):
    """
    Entity-specific interface for Transaction persistence.
    Primary key: transaction_id (str).
    """

    @abstractmethod
    def find_by_account_id_token(self, account_id_token: str) -> List[Transaction]:
        """
        Return all transactions for a given (tokenised) account.
        Used by FR-05 feature enrichment to build velocity counters.
        """
        ...

    @abstractmethod
    def find_by_decision(self, decision: FraudDecision) -> List[Transaction]:
        """
        Return all transactions with a specific FraudDecision outcome.
        Used by UC11 audit report generation.
        """
        ...

    @abstractmethod
    def find_by_risk_tier(self, risk_tier: RiskTier) -> List[Transaction]:
        """Return all transactions classified at a given RiskTier."""
        ...

    @abstractmethod
    def find_flagged(self) -> List[Transaction]:
        """
        Return all HARD_BLOCK transactions.
        Used by FR-09 fraud case generation pipeline.
        """
        ...


# ══════════════════════════════════════════════════════════════════════════════
# FraudCaseRepository
# ══════════════════════════════════════════════════════════════════════════════

class FraudCaseRepository(Repository[FraudCase, str]):
    """
    Entity-specific interface for FraudCase persistence.
    Primary key: case_id (str).
    """

    @abstractmethod
    def find_by_transaction_id(self, transaction_id: str) -> Optional[FraudCase]:
        """
        Return the FraudCase linked to a given transaction (0..1 relationship).
        Used by CustomerDispute.linkToCase() and UC7 dispute flow.
        """
        ...

    @abstractmethod
    def find_by_status(self, status: CaseStatus) -> List[FraudCase]:
        """
        Return all cases with a given CaseStatus.
        Used by FR-10 analyst dashboard case queue.
        """
        ...

    @abstractmethod
    def find_by_priority(self, priority: CasePriority) -> List[FraudCase]:
        """
        Return all cases with a given CasePriority.
        P1 cases appear at the top of the analyst queue (FR-09).
        """
        ...

    @abstractmethod
    def find_open_cases(self) -> List[FraudCase]:
        """
        Return all cases with status OPEN or IN_REVIEW.
        Used by the analyst dashboard to populate the working queue.
        """
        ...

    @abstractmethod
    def find_by_analyst_id(self, analyst_id: str) -> List[FraudCase]:
        """Return all cases assigned to a specific analyst."""
        ...


# ══════════════════════════════════════════════════════════════════════════════
# MLModelRepository
# ══════════════════════════════════════════════════════════════════════════════

class MLModelRepository(Repository[MLModel, str]):
    """
    Entity-specific interface for MLModel persistence.
    Primary key: model_id (str).
    """

    @abstractmethod
    def find_by_model_name(self, model_name: ModelName) -> List[MLModel]:
        """
        Return all versions of a specific model type (e.g., all XGBoost versions).
        Used by FR-13 retraining pipeline to find the current training lineage.
        """
        ...

    @abstractmethod
    def find_by_stage(self, stage: ModelStage) -> List[MLModel]:
        """Return all models in a given lifecycle stage."""
        ...

    @abstractmethod
    def find_production_models(self) -> List[MLModel]:
        """
        Return all models currently in PRODUCTION stage.
        Used by FR-14 hot-swap: the Model Loader queries this to detect
        new production versions every 60 seconds.
        """
        ...

    @abstractmethod
    def find_by_name_and_stage(self, model_name: ModelName, stage: ModelStage) -> Optional[MLModel]:
        """
        Return the specific model version for a name+stage combination.
        Returns None if no model of that type is in that stage.
        """
        ...


# ══════════════════════════════════════════════════════════════════════════════
# AuditRecordRepository
# ══════════════════════════════════════════════════════════════════════════════

class AuditRecordRepository(Repository[AuditRecord, str]):
    """
    Entity-specific interface for AuditRecord persistence.
    Primary key: audit_id (str).
    AuditRecords are immutable — save() is Create-only (no update semantics).
    """

    @abstractmethod
    def find_by_transaction_id(self, transaction_id: str) -> Optional[AuditRecord]:
        """
        Return the AuditRecord for a transaction (1-to-1 relationship, FR-15).
        Used by UC11 audit report generation.
        """
        ...

    @abstractmethod
    def find_by_decision(self, decision: str) -> List[AuditRecord]:
        """
        Return all audit records where decision == the given value.
        Used by the Compliance Officer to filter reports by decision type.
        """
        ...

    @abstractmethod
    def find_tampered(self, signing_key: str) -> List[AuditRecord]:
        """
        Run integrity checks across all records and return those that fail.
        Implements the daily tamper-detection scan from NFR-S4.
        """
        ...


# ══════════════════════════════════════════════════════════════════════════════
# AccountProfileRepository
# ══════════════════════════════════════════════════════════════════════════════

class AccountProfileRepository(Repository[AccountProfile, str]):
    """
    Entity-specific interface for AccountProfile persistence.
    Primary key: account_id_token (str).
    In production this is backed by Redis for sub-millisecond access (FR-05).
    """

    @abstractmethod
    def find_new_accounts(self) -> List[AccountProfile]:
        """
        Return all profiles where transaction_count < 10 (new account threshold).
        Used to identify accounts receiving population-average baselines (BR-AP1).
        """
        ...

    @abstractmethod
    def find_by_risk_tier_override(self, tier: RiskTier) -> List[AccountProfile]:
        """Return profiles with a manual risk tier override applied."""
        ...


# ══════════════════════════════════════════════════════════════════════════════
# CustomerDisputeRepository
# ══════════════════════════════════════════════════════════════════════════════

class CustomerDisputeRepository(Repository[CustomerDispute, str]):
    """
    Entity-specific interface for CustomerDispute persistence.
    Primary key: dispute_id (str).
    """

    @abstractmethod
    def find_by_transaction_id(self, transaction_id: str) -> Optional[CustomerDispute]:
        """
        Return the dispute for a transaction (enforces uniqueness — BR-CD2).
        Returns None when no dispute has been filed for that transaction.
        """
        ...

    @abstractmethod
    def find_by_status(self, status: DisputeStatus) -> List[CustomerDispute]:
        """Return all disputes in a given status."""
        ...

    @abstractmethod
    def find_open_disputes(self) -> List[CustomerDispute]:
        """
        Return all unresolved disputes (OPEN or UNDER_REVIEW).
        Used by the analyst dashboard and SLA tracker.
        """
        ...

    @abstractmethod
    def find_by_customer_id_token(self, customer_id_token: str) -> List[CustomerDispute]:
        """Return all disputes filed by a specific customer."""
        ...


# ══════════════════════════════════════════════════════════════════════════════
# StepUpChallengeRepository
# ══════════════════════════════════════════════════════════════════════════════

class StepUpChallengeRepository(Repository[StepUpChallenge, str]):
    """
    Entity-specific interface for StepUpChallenge persistence.
    Primary key: challenge_id (str).
    In production OTP state is managed in Redis with TTL enforcement (FR-08).
    """

    @abstractmethod
    def find_by_transaction_id(self, transaction_id: str) -> Optional[StepUpChallenge]:
        """
        Return the active challenge for a transaction.
        Used by the Step-Up Auth API to validate submitted OTPs.
        """
        ...

    @abstractmethod
    def find_by_status(self, status: ChallengeStatus) -> List[StepUpChallenge]:
        """Return all challenges in a given status."""
        ...

    @abstractmethod
    def find_expired(self) -> List[StepUpChallenge]:
        """
        Return all challenges whose TTL has elapsed but are not yet marked EXPIRED.
        Used by the cleanup job to escalate stale challenges to HARD_BLOCK.
        """
        ...