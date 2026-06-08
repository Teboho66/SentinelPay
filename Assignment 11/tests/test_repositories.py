"""
Tests – In-Memory Repositories (all 7 entities)
==================================================
Tests CRUD operations and domain-specific query methods for every
SentinelPay entity repository.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from repositories.inmemory import (
    InMemoryTransactionRepository,
    InMemoryFraudCaseRepository,
    InMemoryMLModelRepository,
    InMemoryAuditRecordRepository,
    InMemoryAccountProfileRepository,
    InMemoryCustomerDisputeRepository,
    InMemoryStepUpChallengeRepository,
)
from src.models import (
    Transaction,
    FraudCase,
    MLModel,
    AccountProfile,
    CustomerDispute,
    StepUpChallenge,
    GeoPoint,
    TransactionChannel,
    FraudDecision,
    RiskTier,
    CaseStatus,
    CasePriority,
    ModelName,
    ModelStage,
    DisputeStatus,
    ChallengeStatus,
    AuditService,
)


# ══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def geo():
    return GeoPoint(-33.9249, 18.4241)


def make_transaction(
    txn_id: str,
    account_token: str,
    decision: FraudDecision,
    risk_tier: RiskTier,
    geo: GeoPoint,
    amount: Decimal = Decimal("500.00"),
) -> Transaction:
    txn = Transaction(
        transaction_id=txn_id,
        account_id_token=account_token,
        merchant_id="MER-001",
        merchant_category_code="5411",
        amount=amount,
        currency="ZAR",
        channel=TransactionChannel.CNP_ONLINE,
        device_fingerprint_token="dfp_001",
        ip_address_hash="hash001",
        geolocation=geo,
    )
    txn._decision = decision
    txn._risk_tier = risk_tier
    txn._fraud_score = 0.92 if decision == FraudDecision.HARD_BLOCK else 0.15
    txn._model_version_composite = "xgboost-v3.1"
    return txn


@pytest.fixture
def txn_approved(geo):
    return make_transaction(
        "TXN-APPROVED", "acc_001", FraudDecision.APPROVE, RiskTier.LOW, geo
    )


@pytest.fixture
def txn_blocked(geo):
    return make_transaction(
        "TXN-BLOCKED", "acc_002", FraudDecision.HARD_BLOCK, RiskTier.CRITICAL, geo
    )


@pytest.fixture
def txn_soft(geo):
    return make_transaction(
        "TXN-SOFT", "acc_001", FraudDecision.SOFT_DECLINE, RiskTier.MEDIUM, geo
    )


@pytest.fixture
def fraud_case_p1():
    return FraudCase(
        "TXN-BLOCKED", "acc_002", fraud_score=0.93, risk_tier=RiskTier.CRITICAL
    )


@pytest.fixture
def fraud_case_p3():
    return FraudCase(
        "TXN-OTHER", "acc_003", fraud_score=0.60, risk_tier=RiskTier.MEDIUM
    )


@pytest.fixture
def xgb_model():
    return MLModel(
        "xgb-3.1",
        ModelName.XGBOOST,
        "3.1",
        "mlflow://xgb/3.1",
        "tabular-v3",
        precision=0.91,
        recall=0.87,
        stage=ModelStage.PRODUCTION,
    )


@pytest.fixture
def iso_model():
    return MLModel(
        "iso-2.0",
        ModelName.ISOLATION_FOREST,
        "2.0",
        "mlflow://iso/2.0",
        "tabular-v2",
        precision=0.86,
        recall=0.82,
        stage=ModelStage.PRODUCTION,
    )


@pytest.fixture
def staging_model():
    return MLModel(
        "xgb-4.0",
        ModelName.XGBOOST,
        "4.0",
        "mlflow://xgb/4.0",
        "tabular-v3",
        precision=0.88,
        recall=0.84,
        stage=ModelStage.STAGING,
    )


@pytest.fixture
def audit_record(txn_blocked):
    service = AuditService("test-signing-key")
    return service.write_audit_record(txn_blocked)


@pytest.fixture
def account_profile_new():
    return AccountProfile(
        "acc_token_new", avg_amount_30d=Decimal("0"), transaction_count=3
    )


@pytest.fixture
def account_profile_established():
    return AccountProfile(
        "acc_token_est", avg_amount_30d=Decimal("1200.00"), transaction_count=45
    )


@pytest.fixture
def dispute():
    return CustomerDispute(
        transaction_id="TXN-BLOCKED",
        customer_id_token="cust_token_001",
        transaction_date=datetime.utcnow() - timedelta(days=5),
    )


@pytest.fixture
def challenge():
    c = StepUpChallenge(transaction_id="TXN-SOFT")
    c.generate_otp()
    c.deliver_to_customer()
    return c


# ══════════════════════════════════════════════════════════════════════════════
# TransactionRepository Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestInMemoryTransactionRepository:
    def setup_method(self):
        self.repo = InMemoryTransactionRepository()

    def test_save_and_find_by_id(self, txn_approved):
        self.repo.save(txn_approved)
        result = self.repo.find_by_id("TXN-APPROVED")
        assert result is txn_approved

    def test_find_by_id_returns_none_for_missing(self):
        assert self.repo.find_by_id("NONEXISTENT") is None

    def test_find_all_returns_all_saved(self, txn_approved, txn_blocked, txn_soft):
        for t in [txn_approved, txn_blocked, txn_soft]:
            self.repo.save(t)
        assert len(self.repo.find_all()) == 3

    def test_find_all_returns_copy_not_reference(self, txn_approved):
        self.repo.save(txn_approved)
        snapshot = self.repo.find_all()
        snapshot.clear()
        assert self.repo.count() == 1

    def test_delete_removes_entity(self, txn_approved):
        self.repo.save(txn_approved)
        self.repo.delete("TXN-APPROVED")
        assert self.repo.find_by_id("TXN-APPROVED") is None

    def test_delete_is_idempotent(self):
        self.repo.delete("DOES-NOT-EXIST")  # should not raise

    def test_count_reflects_saved_entities(self, txn_approved, txn_blocked):
        self.repo.save(txn_approved)
        self.repo.save(txn_blocked)
        assert self.repo.count() == 2

    def test_exists_true_after_save(self, txn_approved):
        self.repo.save(txn_approved)
        assert self.repo.exists("TXN-APPROVED") is True

    def test_exists_false_before_save(self):
        assert self.repo.exists("TXN-APPROVED") is False

    def test_save_overwrites_existing(self, txn_approved, geo):
        self.repo.save(txn_approved)
        updated = make_transaction(
            "TXN-APPROVED", "acc_001", FraudDecision.HARD_BLOCK, RiskTier.HIGH, geo
        )
        self.repo.save(updated)
        assert self.repo.find_by_id("TXN-APPROVED").decision == FraudDecision.HARD_BLOCK

    def test_find_by_account_id_token(self, txn_approved, txn_soft, txn_blocked):
        for t in [txn_approved, txn_soft, txn_blocked]:
            self.repo.save(t)
        result = self.repo.find_by_account_id_token("acc_001")
        assert len(result) == 2  # txn_approved and txn_soft both have acc_001

    def test_find_by_decision_hard_block(self, txn_approved, txn_blocked):
        self.repo.save(txn_approved)
        self.repo.save(txn_blocked)
        result = self.repo.find_by_decision(FraudDecision.HARD_BLOCK)
        assert len(result) == 1
        assert result[0].transaction_id == "TXN-BLOCKED"

    def test_find_by_risk_tier(self, txn_approved, txn_blocked):
        self.repo.save(txn_approved)
        self.repo.save(txn_blocked)
        result = self.repo.find_by_risk_tier(RiskTier.CRITICAL)
        assert len(result) == 1

    def test_find_flagged_returns_hard_block_only(
        self, txn_approved, txn_blocked, txn_soft
    ):
        for t in [txn_approved, txn_blocked, txn_soft]:
            self.repo.save(t)
        result = self.repo.find_flagged()
        assert all(t.decision == FraudDecision.HARD_BLOCK for t in result)


# ══════════════════════════════════════════════════════════════════════════════
# FraudCaseRepository Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestInMemoryFraudCaseRepository:
    def setup_method(self):
        self.repo = InMemoryFraudCaseRepository()

    def test_save_and_find_by_id(self, fraud_case_p1):
        self.repo.save(fraud_case_p1)
        result = self.repo.find_by_id(fraud_case_p1.case_id)
        assert result is fraud_case_p1

    def test_find_by_transaction_id(self, fraud_case_p1):
        self.repo.save(fraud_case_p1)
        result = self.repo.find_by_transaction_id("TXN-BLOCKED")
        assert result is fraud_case_p1

    def test_find_by_transaction_id_returns_none_when_missing(self):
        assert self.repo.find_by_transaction_id("TXN-MISSING") is None

    def test_find_by_status_open(self, fraud_case_p1, fraud_case_p3):
        self.repo.save(fraud_case_p1)
        self.repo.save(fraud_case_p3)
        fraud_case_p3.assign_to_analyst("analyst_001")  # moves to IN_REVIEW
        result = self.repo.find_by_status(CaseStatus.OPEN)
        assert any(c.case_id == fraud_case_p1.case_id for c in result)

    def test_find_by_priority_p1(self, fraud_case_p1, fraud_case_p3):
        self.repo.save(fraud_case_p1)
        self.repo.save(fraud_case_p3)
        result = self.repo.find_by_priority(CasePriority.P1)
        assert len(result) == 1
        assert result[0].case_id == fraud_case_p1.case_id

    def test_find_open_cases_includes_in_review(self, fraud_case_p1, fraud_case_p3):
        self.repo.save(fraud_case_p1)
        self.repo.save(fraud_case_p3)
        fraud_case_p3.assign_to_analyst("analyst_001")
        open_cases = self.repo.find_open_cases()
        statuses = {c.status for c in open_cases}
        assert CaseStatus.OPEN in statuses or CaseStatus.IN_REVIEW in statuses

    def test_find_by_analyst_id(self, fraud_case_p1):
        fraud_case_p1.assign_to_analyst("j.mokoena")
        self.repo.save(fraud_case_p1)
        result = self.repo.find_by_analyst_id("j.mokoena")
        assert len(result) == 1

    def test_delete_case(self, fraud_case_p1):
        self.repo.save(fraud_case_p1)
        self.repo.delete(fraud_case_p1.case_id)
        assert self.repo.find_by_id(fraud_case_p1.case_id) is None


# ══════════════════════════════════════════════════════════════════════════════
# MLModelRepository Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestInMemoryMLModelRepository:
    def setup_method(self):
        self.repo = InMemoryMLModelRepository()

    def test_save_and_find_by_id(self, xgb_model):
        self.repo.save(xgb_model)
        assert self.repo.find_by_id("xgb-3.1") is xgb_model

    def test_find_production_models(self, xgb_model, iso_model, staging_model):
        for m in [xgb_model, iso_model, staging_model]:
            self.repo.save(m)
        prod = self.repo.find_production_models()
        assert len(prod) == 2
        assert all(m.stage == ModelStage.PRODUCTION for m in prod)

    def test_find_by_model_name(self, xgb_model, staging_model, iso_model):
        for m in [xgb_model, staging_model, iso_model]:
            self.repo.save(m)
        result = self.repo.find_by_model_name(ModelName.XGBOOST)
        assert len(result) == 2  # xgb-3.1 and xgb-4.0

    def test_find_by_stage_staging(self, xgb_model, staging_model):
        self.repo.save(xgb_model)
        self.repo.save(staging_model)
        result = self.repo.find_by_stage(ModelStage.STAGING)
        assert len(result) == 1
        assert result[0].model_id == "xgb-4.0"

    def test_find_by_name_and_stage(self, xgb_model, staging_model):
        self.repo.save(xgb_model)
        self.repo.save(staging_model)
        result = self.repo.find_by_name_and_stage(
            ModelName.XGBOOST, ModelStage.PRODUCTION
        )
        assert result is xgb_model

    def test_find_by_name_and_stage_returns_none_when_missing(self, xgb_model):
        self.repo.save(xgb_model)
        result = self.repo.find_by_name_and_stage(
            ModelName.DISTILBERT, ModelStage.PRODUCTION
        )
        assert result is None

    def test_count(self, xgb_model, iso_model):
        self.repo.save(xgb_model)
        self.repo.save(iso_model)
        assert self.repo.count() == 2


# ══════════════════════════════════════════════════════════════════════════════
# AuditRecordRepository Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestInMemoryAuditRecordRepository:
    def setup_method(self):
        self.repo = InMemoryAuditRecordRepository()

    def test_save_and_find_by_id(self, audit_record):
        self.repo.save(audit_record)
        result = self.repo.find_by_id(audit_record.audit_id)
        assert result is audit_record

    def test_find_by_transaction_id(self, audit_record):
        self.repo.save(audit_record)
        result = self.repo.find_by_transaction_id("TXN-BLOCKED")
        assert result is audit_record

    def test_find_by_decision(self, audit_record):
        self.repo.save(audit_record)
        result = self.repo.find_by_decision(FraudDecision.HARD_BLOCK.value)
        assert len(result) == 1

    def test_delete_raises_runtime_error(self, audit_record):
        self.repo.save(audit_record)
        with pytest.raises(RuntimeError, match="BR-AR2"):
            self.repo.delete(audit_record.audit_id)

    def test_find_tampered_empty_when_all_valid(self, audit_record):
        self.repo.save(audit_record)
        tampered = self.repo.find_tampered("test-signing-key")
        assert tampered == []

    def test_find_tampered_detects_corrupted_record(self, audit_record):
        self.repo.save(audit_record)
        # Corrupt the stored hash to simulate tampering
        audit_record._record_hash = (
            "0000000000000000000000000000000000000000000000000000000000000000"
        )
        tampered = self.repo.find_tampered("test-signing-key")
        assert len(tampered) == 1


# ══════════════════════════════════════════════════════════════════════════════
# AccountProfileRepository Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestInMemoryAccountProfileRepository:
    def setup_method(self):
        self.repo = InMemoryAccountProfileRepository()

    def test_save_and_find_by_id(self, account_profile_new):
        self.repo.save(account_profile_new)
        result = self.repo.find_by_id("acc_token_new")
        assert result is account_profile_new

    def test_find_new_accounts(self, account_profile_new, account_profile_established):
        self.repo.save(account_profile_new)
        self.repo.save(account_profile_established)
        new_accounts = self.repo.find_new_accounts()
        assert len(new_accounts) == 1
        assert new_accounts[0].account_id_token == "acc_token_new"

    def test_established_account_not_in_new_accounts(self, account_profile_established):
        self.repo.save(account_profile_established)
        assert self.repo.find_new_accounts() == []

    def test_count_and_exists(self, account_profile_new):
        self.repo.save(account_profile_new)
        assert self.repo.count() == 1
        assert self.repo.exists("acc_token_new") is True


# ══════════════════════════════════════════════════════════════════════════════
# CustomerDisputeRepository Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestInMemoryCustomerDisputeRepository:
    def setup_method(self):
        self.repo = InMemoryCustomerDisputeRepository()

    def test_save_and_find_by_id(self, dispute):
        self.repo.save(dispute)
        result = self.repo.find_by_id(dispute.dispute_id)
        assert result is dispute

    def test_find_by_transaction_id(self, dispute):
        self.repo.save(dispute)
        result = self.repo.find_by_transaction_id("TXN-BLOCKED")
        assert result is dispute

    def test_find_by_transaction_id_returns_none_when_missing(self):
        assert self.repo.find_by_transaction_id("TXN-NONE") is None

    def test_find_open_disputes(self, dispute):
        self.repo.save(dispute)
        open_disputes = self.repo.find_open_disputes()
        assert len(open_disputes) == 1

    def test_find_by_status_resolved(self, dispute):
        dispute.link_to_case("CASE-001")
        dispute.resolve(DisputeStatus.RESOLVED_FALSE_POSITIVE)
        self.repo.save(dispute)
        result = self.repo.find_by_status(DisputeStatus.RESOLVED_FALSE_POSITIVE)
        assert len(result) == 1

    def test_resolved_dispute_not_in_open(self, dispute):
        dispute.link_to_case("CASE-001")
        dispute.resolve(DisputeStatus.RESOLVED_FRAUD)
        self.repo.save(dispute)
        assert self.repo.find_open_disputes() == []

    def test_delete_dispute(self, dispute):
        self.repo.save(dispute)
        self.repo.delete(dispute.dispute_id)
        assert self.repo.find_by_id(dispute.dispute_id) is None


# ══════════════════════════════════════════════════════════════════════════════
# StepUpChallengeRepository Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestInMemoryStepUpChallengeRepository:
    def setup_method(self):
        self.repo = InMemoryStepUpChallengeRepository()

    def test_save_and_find_by_id(self, challenge):
        self.repo.save(challenge)
        result = self.repo.find_by_id(challenge.challenge_id)
        assert result is challenge

    def test_find_by_transaction_id(self, challenge):
        self.repo.save(challenge)
        result = self.repo.find_by_transaction_id("TXN-SOFT")
        assert result is challenge

    def test_find_by_status_delivered(self, challenge):
        self.repo.save(challenge)
        result = self.repo.find_by_status(ChallengeStatus.DELIVERED)
        assert len(result) == 1

    def test_find_expired_returns_timed_out_challenges(self):
        # Create challenge with TTL of 0 (immediately expired)
        expired = StepUpChallenge(transaction_id="TXN-EXPIRED", ttl_seconds=0)
        expired.generate_otp()
        expired.deliver_to_customer()
        self.repo.save(expired)
        result = self.repo.find_expired()
        assert len(result) == 1

    def test_completed_challenge_not_in_expired(self, challenge):
        raw_otp = challenge.generate_otp()
        challenge.validate_otp(raw_otp)
        self.repo.save(challenge)
        assert self.repo.find_expired() == []

    def test_count_and_exists(self, challenge):
        self.repo.save(challenge)
        assert self.repo.count() == 1
        assert self.repo.exists(challenge.challenge_id) is True
