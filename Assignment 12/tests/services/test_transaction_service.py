"""
Tests – TransactionService
============================
Unit tests for all business logic in TransactionService.
Uses InMemoryTransactionRepository — no HTTP layer involved.
"""

import pytest
from decimal import Decimal

import sys
import os

for _p in ("../Assignment10", "../Assignment11"):
    _abs = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../" + _p.lstrip("../"))
    )
    if _abs not in sys.path:
        sys.path.insert(0, _abs)

from repositories.inmemory import InMemoryTransactionRepository
from services import (
    TransactionService,
    EntityNotFoundError,
    DuplicateEntityError,
    BusinessRuleViolationError,
    InvalidStateTransitionError,
)
from src.models import FraudDecision


@pytest.fixture
def repo():
    return InMemoryTransactionRepository()


@pytest.fixture
def service(repo):
    return TransactionService(repo)


def submit(
    service,
    txn_id="TXN-001",
    account="acc_001",
    amount=Decimal("500.00"),
    channel="CNP_ONLINE",
):
    return service.submit_transaction(
        transaction_id=txn_id,
        account_id_token=account,
        merchant_id="MER-001",
        merchant_category_code="5411",
        amount=amount,
        currency="ZAR",
        channel=channel,
        device_fingerprint_token="dfp_abc",
        ip_address_hash="hash_abc",
        latitude=-33.9249,
        longitude=18.4241,
    )


MODEL_SCORES = [
    {
        "model_name": "XGBOOST",
        "model_version": "3.1",
        "raw_score": 0.88,
        "confidence": 0.92,
    },
    {
        "model_name": "ISOLATION_FOREST",
        "model_version": "2.0",
        "raw_score": 0.75,
        "confidence": 0.80,
    },
    {
        "model_name": "DISTILBERT",
        "model_version": "1.4",
        "raw_score": 0.70,
        "confidence": 0.78,
    },
]


class TestSubmitTransaction:
    def test_submit_creates_transaction(self, service):
        txn = submit(service)
        assert txn.transaction_id == "TXN-001"

    def test_pii_tokenised_on_submit(self, service):
        txn = submit(service)
        assert txn.pii_tokenised is True

    def test_account_token_prefixed_after_tokenisation(self, service):
        txn = submit(service)
        assert txn.account_id_token.startswith("acc_token_")

    def test_duplicate_transaction_id_raises_409(self, service):
        submit(service)
        with pytest.raises(DuplicateEntityError):
            submit(service)

    def test_negative_amount_raises(self, service):
        with pytest.raises(ValueError):
            submit(service, amount=Decimal("-50.00"))

    def test_invalid_channel_raises_business_rule_error(self, service):
        with pytest.raises(BusinessRuleViolationError, match="FR-02"):
            submit(service, channel="INVALID_CHANNEL")

    def test_invalid_currency_raises(self, service):
        with pytest.raises(ValueError):
            service.submit_transaction(
                "TXN-002",
                "acc_002",
                "MER-001",
                "5411",
                Decimal("100.00"),
                "RAND",
                "CNP_ONLINE",
                "dfp_abc",
                "hash_abc",
                -33.9,
                18.4,
            )

    def test_transaction_persisted_in_repo(self, service, repo):
        submit(service)
        assert repo.exists("TXN-001")


class TestApplyFraudDecision:
    def test_apply_decision_sets_decision(self, service):
        submit(service)
        txn = service.apply_fraud_decision("TXN-001", 0.87, MODEL_SCORES)
        assert txn.decision is not None

    def test_high_fraud_score_produces_hard_block(self, service):
        submit(service)
        scores = [
            {
                "model_name": "XGBOOST",
                "model_version": "3.1",
                "raw_score": 0.95,
                "confidence": 0.98,
            }
        ]
        txn = service.apply_fraud_decision("TXN-001", 0.95, scores, "STANDARD")
        assert txn.decision == FraudDecision.HARD_BLOCK

    def test_low_fraud_score_produces_approve(self, service):
        submit(service)
        scores = [
            {
                "model_name": "XGBOOST",
                "model_version": "3.1",
                "raw_score": 0.10,
                "confidence": 0.95,
            }
        ]
        txn = service.apply_fraud_decision("TXN-001", 0.10, scores, "STANDARD")
        assert txn.decision == FraudDecision.APPROVE

    def test_mid_fraud_score_produces_soft_decline(self, service):
        submit(service)
        scores = [
            {
                "model_name": "XGBOOST",
                "model_version": "3.1",
                "raw_score": 0.55,
                "confidence": 0.80,
            }
        ]
        txn = service.apply_fraud_decision("TXN-001", 0.55, scores, "STANDARD")
        assert txn.decision == FraudDecision.SOFT_DECLINE

    def test_decision_already_applied_raises_409(self, service):
        submit(service)
        service.apply_fraud_decision("TXN-001", 0.87, MODEL_SCORES)
        with pytest.raises(InvalidStateTransitionError):
            service.apply_fraud_decision("TXN-001", 0.50, MODEL_SCORES)

    def test_decision_on_missing_transaction_raises_404(self, service):
        with pytest.raises(EntityNotFoundError):
            service.apply_fraud_decision("NONEXISTENT", 0.5, MODEL_SCORES)


class TestQueryOperations:
    def test_get_transaction_returns_entity(self, service):
        submit(service)
        txn = service.get_transaction("TXN-001")
        assert txn.transaction_id == "TXN-001"

    def test_get_nonexistent_raises_404(self, service):
        with pytest.raises(EntityNotFoundError):
            service.get_transaction("MISSING")

    def test_get_all_returns_all(self, service):
        submit(service, "TXN-001")
        submit(service, "TXN-002")
        assert len(service.get_all_transactions()) == 2

    def test_get_flagged_returns_hard_blocks_only(self, service):
        submit(service, "TXN-001")
        submit(service, "TXN-002")
        scores_high = [
            {
                "model_name": "XGBOOST",
                "model_version": "3.1",
                "raw_score": 0.95,
                "confidence": 0.98,
            }
        ]
        scores_low = [
            {
                "model_name": "XGBOOST",
                "model_version": "3.1",
                "raw_score": 0.05,
                "confidence": 0.99,
            }
        ]
        service.apply_fraud_decision("TXN-001", 0.95, scores_high)
        service.apply_fraud_decision("TXN-002", 0.05, scores_low)
        flagged = service.get_flagged_transactions()
        assert all(t.decision == FraudDecision.HARD_BLOCK for t in flagged)

    def test_get_by_invalid_decision_raises_422(self, service):
        with pytest.raises(BusinessRuleViolationError):
            service.get_by_decision("INVALID")

    def test_get_by_invalid_risk_tier_raises_422(self, service):
        with pytest.raises(BusinessRuleViolationError):
            service.get_by_risk_tier("EXTREME")

    def test_delete_transaction(self, service, repo):
        submit(service)
        service.delete_transaction("TXN-001")
        assert not repo.exists("TXN-001")

    def test_delete_nonexistent_raises_404(self, service):
        with pytest.raises(EntityNotFoundError):
            service.delete_transaction("MISSING")
