"""
Tests – FraudCaseService
==========================
Unit tests for all business logic in FraudCaseService.
"""

import pytest
from repositories.inmemory import InMemoryFraudCaseRepository
from services import (
    FraudCaseService,
    EntityNotFoundError,
    DuplicateEntityError,
    BusinessRuleViolationError,
    InvalidStateTransitionError,
)
from src.models import CaseStatus, CasePriority


@pytest.fixture
def repo():
    return InMemoryFraudCaseRepository()


@pytest.fixture
def service(repo):
    return FraudCaseService(repo)


def create(service, txn_id="TXN-001", fraud_score=0.93, risk_tier="CRITICAL"):
    return service.create_case(
        transaction_id=txn_id,
        account_id_token="acc_token_001",
        fraud_score=fraud_score,
        risk_tier=risk_tier,
    )


class TestCreateCase:
    def test_creates_case_for_critical_tier(self, service):
        case = create(service, risk_tier="CRITICAL")
        assert case is not None

    def test_creates_case_for_high_tier(self, service):
        case = create(service, risk_tier="HIGH", fraud_score=0.70)
        assert case is not None

    def test_low_tier_raises_422(self, service):
        with pytest.raises(BusinessRuleViolationError, match="FR-09"):
            create(service, risk_tier="LOW", fraud_score=0.20)

    def test_medium_tier_raises_422(self, service):
        with pytest.raises(BusinessRuleViolationError, match="FR-09"):
            create(service, risk_tier="MEDIUM", fraud_score=0.50)

    def test_duplicate_transaction_id_raises_409(self, service):
        create(service)
        with pytest.raises(DuplicateEntityError):
            create(service)

    def test_p1_priority_for_score_above_090(self, service):
        case = create(service, fraud_score=0.95)
        assert case.priority == CasePriority.P1

    def test_p2_priority_for_score_between_075_090(self, service):
        case = create(service, fraud_score=0.80, risk_tier="HIGH")
        assert case.priority == CasePriority.P2

    def test_p3_priority_for_score_below_075(self, service):
        case = create(service, fraud_score=0.65, risk_tier="HIGH")
        assert case.priority == CasePriority.P3

    def test_initial_status_is_open(self, service):
        case = create(service)
        assert case.status == CaseStatus.OPEN

    def test_unknown_risk_tier_raises_422(self, service):
        with pytest.raises(BusinessRuleViolationError):
            create(service, risk_tier="EXTREME")


class TestAssignToAnalyst:
    def test_assign_moves_to_in_review(self, service):
        case = create(service)
        case = service.assign_to_analyst(case.case_id, "j.mokoena")
        assert case.status == CaseStatus.IN_REVIEW

    def test_assign_stores_analyst_id(self, service):
        case = create(service)
        case = service.assign_to_analyst(case.case_id, "j.mokoena")
        assert case.assigned_analyst_id == "j.mokoena"

    def test_assign_to_nonexistent_raises_404(self, service):
        with pytest.raises(EntityNotFoundError):
            service.assign_to_analyst("CASE-MISSING", "j.mokoena")

    def test_blank_analyst_id_raises_422(self, service):
        case = create(service)
        with pytest.raises(BusinessRuleViolationError):
            service.assign_to_analyst(case.case_id, "   ")

    def test_assign_to_confirmed_case_raises_409(self, service):
        case = create(service)
        service.assign_to_analyst(case.case_id, "j.mokoena")
        service.resolve_case(case.case_id, "CONFIRMED", "Confirmed fraud.")
        with pytest.raises(InvalidStateTransitionError):
            service.assign_to_analyst(case.case_id, "another_analyst")


class TestResolveCase:
    def _get_in_review_case(self, service):
        case = create(service)
        service.assign_to_analyst(case.case_id, "j.mokoena")
        return case

    def test_resolve_confirmed_sets_status(self, service):
        case = self._get_in_review_case(service)
        resolved, _ = service.resolve_case(
            case.case_id, "CONFIRMED", "Fraud confirmed."
        )
        assert resolved.status == CaseStatus.CONFIRMED

    def test_confirmed_returns_fraud_label_payload(self, service):
        case = self._get_in_review_case(service)
        _, payload = service.resolve_case(case.case_id, "CONFIRMED", "Confirmed.")
        assert payload is not None
        assert payload["label"] == "fraud"
        assert payload["transaction_id"] == "TXN-001"

    def test_dismissed_returns_no_label_payload(self, service):
        case = self._get_in_review_case(service)
        _, payload = service.resolve_case(case.case_id, "DISMISSED", "False positive.")
        assert payload is None

    def test_dismissed_without_note_raises_422(self, service):
        case = self._get_in_review_case(service)
        with pytest.raises(BusinessRuleViolationError, match="BR-FC2"):
            service.resolve_case(case.case_id, "DISMISSED", "")

    def test_resolve_open_case_raises_409(self, service):
        case = create(service)
        with pytest.raises(InvalidStateTransitionError):
            service.resolve_case(case.case_id, "CONFIRMED", "Note")

    def test_resolve_nonexistent_raises_404(self, service):
        with pytest.raises(EntityNotFoundError):
            service.resolve_case("MISSING", "CONFIRMED", "Note")


class TestQueryOperations:
    def test_get_analyst_queue_sorted_p1_first(self, service):
        create(service, "TXN-001", fraud_score=0.65, risk_tier="HIGH")  # P3
        create(service, "TXN-002", fraud_score=0.95, risk_tier="CRITICAL")  # P1
        create(service, "TXN-003", fraud_score=0.80, risk_tier="HIGH")  # P2
        queue = service.get_analyst_queue()
        assert queue[0].priority == CasePriority.P1
        assert queue[1].priority == CasePriority.P2
        assert queue[2].priority == CasePriority.P3

    def test_resolved_cases_not_in_queue(self, service):
        case = create(service)
        service.assign_to_analyst(case.case_id, "j.mokoena")
        service.resolve_case(case.case_id, "CONFIRMED", "Confirmed.")
        assert service.get_analyst_queue() == []

    def test_delete_dismissed_case(self, service):
        case = create(service)
        service.assign_to_analyst(case.case_id, "j.mokoena")
        service.resolve_case(
            case.case_id, "DISMISSED", "False positive — customer verified."
        )
        service.delete_case(case.case_id)
        with pytest.raises(EntityNotFoundError):
            service.get_case(case.case_id)

    def test_delete_confirmed_case_raises_422(self, service):
        case = create(service)
        service.assign_to_analyst(case.case_id, "j.mokoena")
        service.resolve_case(case.case_id, "CONFIRMED", "Confirmed fraud.")
        with pytest.raises(BusinessRuleViolationError):
            service.delete_case(case.case_id)

    def test_get_by_invalid_priority_raises_422(self, service):
        with pytest.raises(BusinessRuleViolationError):
            service.get_by_priority("P99")
