"""
SentinelPay – Assignment 12
services/fraud_case_service.py

FraudCaseService
=================
Encapsulates all business logic for FraudCase operations.
Uses FraudCaseRepository (A11) for persistence.

Business rules enforced:
  - FR-09  : One FraudCase per Transaction (duplicate guard)
  - FR-09  : Only HARD_BLOCK + HIGH/CRITICAL risk tier generates a case
  - BR-FC2 : DISMISSED resolution requires non-empty analyst note
  - FR-10  : Case queue sorted P1 → P2 → P3
  - FR-10  : CONFIRMED resolution triggers fraud label publication
  - SLA    : is_breaching_sla() surfaced in queue responses
"""

from __future__ import annotations
import sys, os
for _p in ("../Assignment10", "../Assignment11"):
    _abs = os.path.abspath(os.path.join(os.path.dirname(__file__), _p))
    if _abs not in sys.path:
        sys.path.insert(0, _abs)

from typing import List, Optional

from src.models import (
    FraudCase, RiskTier, FraudDecision,
    CaseStatus, CasePriority,
)
from repositories.interfaces import FraudCaseRepository
from services.exceptions import (
    EntityNotFoundError, DuplicateEntityError,
    BusinessRuleViolationError, InvalidStateTransitionError,
)

# Priority sort order for analyst queue (P1 first)
_PRIORITY_ORDER = {CasePriority.P1: 0, CasePriority.P2: 1, CasePriority.P3: 2}


class FraudCaseService:
    """
    Service layer for FraudCase operations.
    Injected with a FraudCaseRepository — storage-backend agnostic.
    """

    def __init__(self, fraud_case_repo: FraudCaseRepository) -> None:
        self._repo = fraud_case_repo

    # ── Command operations ────────────────────────────────────────────────────

    def create_case(
        self,
        transaction_id: str,
        account_id_token: str,
        fraud_score: float,
        risk_tier: str,
        shap_report_ref: str = "",
    ) -> FraudCase:
        """
        FR-09: Create a fraud investigation case.

        Business rules:
          - Only HARD_BLOCK + HIGH or CRITICAL risk tier → BusinessRuleViolationError
          - One case per transaction_id → DuplicateEntityError (BR-CD2 equivalent)
        """
        # Validate risk tier
        try:
            # Validate risk tier
            risk_tier_value = risk_tier.upper()

            if hasattr(RiskTier, risk_tier_value):
               tier_enum = getattr(RiskTier, risk_tier_value)
            else:
                raise BusinessRuleViolationError(
                    "FR-09",
                     f"Unknown risk tier '{risk_tier}'.",
    )
        except KeyError:
            raise BusinessRuleViolationError(
                "FR-09",
                f"Unknown risk tier '{risk_tier}'. Valid: {[r.name for r in RiskTier]}"
            )

        # FR-09: only HIGH / CRITICAL generate a case
        if tier_enum not in (RiskTier.HIGH, RiskTier.CRITICAL):
            raise BusinessRuleViolationError(
                "FR-09",
                f"FraudCase only generated for HIGH or CRITICAL risk tier. "
                f"Received: {risk_tier}. LOW and MEDIUM transactions do not generate cases."
            )

        # One case per transaction
        existing = self._repo.find_by_transaction_id(transaction_id)
        if existing is not None:
            raise DuplicateEntityError(
                "FraudCase", "transaction_id", transaction_id
            )

        case = FraudCase(
            transaction_id=transaction_id,
            account_id_token=account_id_token,
            fraud_score=fraud_score,
            risk_tier=tier_enum,
            shap_report_ref=shap_report_ref,
        )
        self._repo.save(case)
        return case

    def assign_to_analyst(self, case_id: str, analyst_id: str) -> FraudCase:
        """
        FR-10: Assign an OPEN case to a fraud analyst.

        Business rules:
          - Case must exist → EntityNotFoundError
          - Case must be OPEN (not already resolved) → InvalidStateTransitionError
          - analyst_id must not be blank → BusinessRuleViolationError
        """
        case = self._get_or_404(case_id)

        if case.status not in (CaseStatus.OPEN, CaseStatus.IN_REVIEW):
            raise InvalidStateTransitionError(
                "FraudCase", case.status.value, "assign_to_analyst"
            )

        if not analyst_id.strip():
            raise BusinessRuleViolationError(
                "FR-10", "analyst_id cannot be blank."
            )

        case.assign_to_analyst(analyst_id)
        self._repo.save(case)
        return case

    def resolve_case(
        self, case_id: str, resolution: str, note: str = ""
    ) -> FraudCase:
        """
        FR-10: Resolve a case as CONFIRMED or DISMISSED.

        Business rules:
          - Case must be IN_REVIEW → InvalidStateTransitionError
          - DISMISSED requires non-empty note (BR-FC2)
          - CONFIRMED publishes fraud label payload (BR-FC3)
        """
        case = self._get_or_404(case_id)

        if case.status != CaseStatus.IN_REVIEW:
            raise InvalidStateTransitionError(
                "FraudCase", case.status.value, f"resolve as {resolution}"
            )

        try:
            resolution_enum = CaseStatus[resolution.upper()]
        except KeyError:
            raise BusinessRuleViolationError(
                "FR-10",
                f"Invalid resolution '{resolution}'. Must be CONFIRMED or DISMISSED."
            )

        # BR-FC2: note required for DISMISSED
        if resolution_enum == CaseStatus.DISMISSED and not note.strip():
            raise BusinessRuleViolationError(
                "BR-FC2",
                "A non-empty analyst note is required for DISMISSED (FALSE_POSITIVE) resolutions."
            )

        case.resolve(resolution_enum, note)
        self._repo.save(case)

        # BR-FC3: if confirmed, publish fraud label (returned in response)
        label_payload = None
        if resolution_enum == CaseStatus.CONFIRMED:
            label_payload = case.publish_fraud_label()

        return case, label_payload

    # ── Query operations ──────────────────────────────────────────────────────

    def get_case(self, case_id: str) -> FraudCase:
        """Return a case by ID or raise EntityNotFoundError (→ 404)."""
        return self._get_or_404(case_id)

    def get_all_cases(self) -> List[FraudCase]:
        """Return all persisted fraud cases."""
        return self._repo.find_all()

    def get_analyst_queue(self) -> List[FraudCase]:
        """
        FR-10: Return open and in-review cases sorted P1 → P2 → P3.
        SLA-breaching cases are flagged (is_breaching_sla()) but not excluded.
        """
        cases = self._repo.find_open_cases()
        return sorted(cases, key=lambda c: _PRIORITY_ORDER.get(c.priority, 99))

    def get_by_priority(self, priority: str) -> List[FraudCase]:
        """FR-09: Return all cases with the given priority level."""
        try:
            priority_enum = CasePriority[priority.upper()]
        except KeyError:
            raise BusinessRuleViolationError(
                "FR-09",
                f"Unknown priority '{priority}'. Valid: {[p.name for p in CasePriority]}"
            )
        return self._repo.find_by_priority(priority_enum)

    def get_by_status(self, status: str) -> List[FraudCase]:
        """Return all cases with the given status."""
        try:
            status_enum = CaseStatus[status.upper()]
        except KeyError:
            raise BusinessRuleViolationError(
                "FR-10",
                f"Unknown status '{status}'. Valid: {[s.name for s in CaseStatus]}"
            )
        return self._repo.find_by_status(status_enum)

    def get_case_for_transaction(self, transaction_id: str) -> FraudCase:
        """Return the case linked to a transaction, or raise EntityNotFoundError."""
        case = self._repo.find_by_transaction_id(transaction_id)
        if case is None:
            raise EntityNotFoundError("FraudCase", f"transaction:{transaction_id}")
        return case

    def delete_case(self, case_id: str) -> None:
        """Remove a case. Only DISMISSED cases should be deletable in production."""
        case = self._get_or_404(case_id)
        if case.status == CaseStatus.CONFIRMED:
            raise BusinessRuleViolationError(
                "FR-09",
                "CONFIRMED fraud cases cannot be deleted — they feed the retraining pipeline."
            )
        self._repo.delete(case_id)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _get_or_404(self, case_id: str) -> FraudCase:
        case = self._repo.find_by_id(case_id)
        if case is None:
            raise EntityNotFoundError("FraudCase", case_id)
        return case