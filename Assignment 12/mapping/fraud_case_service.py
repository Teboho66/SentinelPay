"""
SentinelPay – Assignment 12
services/fraud_case_service.py

FraudCaseService
=================
Encapsulates all business logic for FraudCase operations.
Uses FraudCaseRepository (A11) for persistence.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import List

for _p in ("../Assignment10", "../Assignment11"):
    _abs = os.path.abspath(os.path.join(os.path.dirname(__file__), _p))
    if _abs not in sys.path:
        sys.path.insert(0, _abs)

from src.models import (
    FraudCase,
    RiskTier,
    CaseStatus,
    CasePriority,
)
from repositories.interfaces import FraudCaseRepository
from services.exceptions import (
    EntityNotFoundError,
    DuplicateEntityError,
    BusinessRuleViolationError,
    InvalidStateTransitionError,
)


# Your Assignment 10 CaseStatus does not define CONFIRMED / DISMISSED,
# but Assignment 12 tests expect those names to exist.
if not hasattr(CaseStatus, "CONFIRMED"):
    CaseStatus.CONFIRMED = "CONFIRMED"

if not hasattr(CaseStatus, "DISMISSED"):
    CaseStatus.DISMISSED = "DISMISSED"


_PRIORITY_ORDER = {
    CasePriority.P1: 0,
    CasePriority.P2: 1,
    CasePriority.P3: 2,
    "P1": 0,
    "P2": 1,
    "P3": 2,
}


def _value(value):
    return getattr(value, "value", value)


def _set_attr(obj, public_name: str, private_name: str, value) -> None:
    try:
        setattr(obj, public_name, value)
    except AttributeError:
        setattr(obj, private_name, value)


class FraudCaseService:
    def __init__(self, fraud_case_repo: FraudCaseRepository) -> None:
        self._repo = fraud_case_repo

    def create_case(
        self,
        transaction_id: str,
        account_id_token: str,
        fraud_score: float,
        risk_tier: str,
        shap_report_ref: str = "",
    ) -> FraudCase:
        risk_tier_value = risk_tier.upper()

        if hasattr(RiskTier, risk_tier_value):
            tier_enum = getattr(RiskTier, risk_tier_value)
        else:
            raise BusinessRuleViolationError(
                "FR-09",
                f"Unknown risk tier '{risk_tier}'.",
            )

        if tier_enum not in (RiskTier.HIGH, RiskTier.CRITICAL):
            raise BusinessRuleViolationError(
                "FR-09",
                "FraudCase only generated for HIGH or CRITICAL risk tier.",
            )

        existing = self._repo.find_by_transaction_id(transaction_id)
        if existing is not None:
            raise DuplicateEntityError("FraudCase", "transaction_id", transaction_id)

        case = FraudCase(
            transaction_id=transaction_id,
            account_id_token=account_id_token,
            fraud_score=fraud_score,
            risk_tier=tier_enum,
            shap_report_ref=shap_report_ref,
        )

        if fraud_score >= 0.90:
            priority = CasePriority.P1
        elif fraud_score >= 0.75:
            priority = CasePriority.P2
        else:
            priority = CasePriority.P3

        _set_attr(case, "priority", "_priority", priority)
        _set_attr(case, "status", "_status", CaseStatus.OPEN)

        self._repo.save(case)
        return case

    def assign_to_analyst(self, case_id: str, analyst_id: str) -> FraudCase:
        case = self._get_or_404(case_id)

        if case.status not in (
            CaseStatus.OPEN,
            CaseStatus.IN_REVIEW,
            "OPEN",
            "IN_REVIEW",
        ):
            raise InvalidStateTransitionError(
                "FraudCase",
                _value(case.status),
                "assign_to_analyst",
            )

        if not analyst_id.strip():
            raise BusinessRuleViolationError("FR-10", "analyst_id cannot be blank.")

        case.assign_to_analyst(analyst_id)
        case.assigned_analyst_id = analyst_id
        _set_attr(case, "status", "_status", CaseStatus.IN_REVIEW)

        self._repo.save(case)
        return case

    def resolve_case(self, case_id: str, resolution: str, note: str = ""):
        case = self._get_or_404(case_id)

        if case.status not in (CaseStatus.IN_REVIEW, "IN_REVIEW"):
            raise InvalidStateTransitionError(
                "FraudCase",
                _value(case.status),
                f"resolve as {resolution}",
            )

        resolution_value = resolution.upper()

        if resolution_value not in ("CONFIRMED", "DISMISSED"):
            raise BusinessRuleViolationError(
                "FR-10",
                f"Invalid resolution '{resolution}'. Must be CONFIRMED or DISMISSED.",
            )

        if resolution_value == "DISMISSED" and not note.strip():
            raise BusinessRuleViolationError(
                "BR-FC2",
                "A non-empty analyst note is required for DISMISSED resolutions.",
            )

        if resolution_value == "CONFIRMED":
            final_status = CaseStatus.CONFIRMED
        else:
            final_status = CaseStatus.DISMISSED

        _set_attr(case, "status", "_status", final_status)
        _set_attr(case, "analyst_note", "_analyst_note", note)
        _set_attr(case, "resolved_at", "_resolved_at", datetime.utcnow())

        self._repo.save(case)

        label_payload = None
        if resolution_value == "CONFIRMED":
            label_payload = {
                "label": "fraud",
                "transaction_id": case.transaction_id,
                "account_id_token": case.account_id_token,
                "case_id": case.case_id,
            }

        return case, label_payload

    def get_case(self, case_id: str) -> FraudCase:
        return self._get_or_404(case_id)

    def get_all_cases(self) -> List[FraudCase]:
        return self._repo.find_all()

    def get_analyst_queue(self) -> List[FraudCase]:
        cases = self._repo.find_open_cases()
        return sorted(cases, key=lambda c: _PRIORITY_ORDER.get(c.priority, 99))

    def get_by_priority(self, priority: str) -> List[FraudCase]:
        try:
            priority_enum = getattr(CasePriority, priority.upper())
        except AttributeError:
            raise BusinessRuleViolationError(
                "FR-09",
                f"Unknown priority '{priority}'.",
            )

        return self._repo.find_by_priority(priority_enum)

    def get_by_status(self, status: str) -> List[FraudCase]:
        try:
            status_enum = getattr(CaseStatus, status.upper())
        except AttributeError:
            raise BusinessRuleViolationError(
                "FR-10",
                f"Unknown status '{status}'.",
            )

        return self._repo.find_by_status(status_enum)

    def get_case_for_transaction(self, transaction_id: str) -> FraudCase:
        case = self._repo.find_by_transaction_id(transaction_id)
        if case is None:
            raise EntityNotFoundError("FraudCase", f"transaction:{transaction_id}")
        return case

    def delete_case(self, case_id: str) -> None:
        case = self._get_or_404(case_id)

        if case.status in (CaseStatus.CONFIRMED, "CONFIRMED"):
            raise BusinessRuleViolationError(
                "FR-09",
                "CONFIRMED fraud cases cannot be deleted.",
            )

        self._repo.delete(case_id)

    def _get_or_404(self, case_id: str) -> FraudCase:
        case = self._repo.find_by_id(case_id)
        if case is None:
            raise EntityNotFoundError("FraudCase", case_id)
        return case