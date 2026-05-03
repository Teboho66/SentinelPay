"""
Tests – Builder (FraudCaseBuilder)
====================================
Covers:
  - Happy-path: full build produces a valid FraudCase
  - Missing required fields raise ValueError
  - Priority is auto-derived from RiskScore
  - Escalation flag is false by default
  - Manual priority override works
  - Blank case_id raises ValueError
  - Audit trail accumulates correctly
  - Invalid types for with_transaction / with_alert raise TypeError
"""

import pytest
from creational_patterns.builder import FraudCaseBuilder, FraudCase
from src.models import (
    Transaction,
    TransactionType,
    FraudAlert,
    AlertSeverity,
    RiskScore,
    AuditLog,
    RiskLevel,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_transaction():
    return Transaction(
        amount=85_000.0,
        currency="ZAR",
        transaction_type=TransactionType.WIRE_TRANSFER,
        merchant_id="MER-001",
        account_id="ACC-001",
    )


@pytest.fixture
def sample_alert():
    return FraudAlert(
        transaction_id="TXN-001",
        alert_type="GEO_ANOMALY",
        severity=AlertSeverity.CRITICAL,
        description="Geographic anomaly detected.",
    )


@pytest.fixture
def sample_risk_score_critical():
    return RiskScore(score=0.92, factors=["GEO_ANOMALY", "HIGH_AMOUNT"])


@pytest.fixture
def sample_risk_score_low():
    return RiskScore(score=0.15, factors=["FIRST_TIME_MERCHANT"])


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestFraudCaseBuilder:

    def test_full_build_returns_fraud_case(
        self, sample_transaction, sample_alert, sample_risk_score_critical
    ):
        case = (
            FraudCaseBuilder("CASE-001")
            .with_transaction(sample_transaction)
            .with_alert(sample_alert)
            .with_risk_score(sample_risk_score_critical)
            .build()
        )
        assert isinstance(case, FraudCase)

    def test_missing_transaction_raises_value_error(
        self, sample_alert, sample_risk_score_critical
    ):
        with pytest.raises(ValueError, match="transaction"):
            (
                FraudCaseBuilder("CASE-002")
                .with_alert(sample_alert)
                .with_risk_score(sample_risk_score_critical)
                .build()
            )

    def test_missing_alert_raises_value_error(
        self, sample_transaction, sample_risk_score_critical
    ):
        with pytest.raises(ValueError, match="alert"):
            (
                FraudCaseBuilder("CASE-003")
                .with_transaction(sample_transaction)
                .with_risk_score(sample_risk_score_critical)
                .build()
            )

    def test_missing_risk_score_raises_value_error(
        self, sample_transaction, sample_alert
    ):
        with pytest.raises(ValueError, match="risk_score"):
            (
                FraudCaseBuilder("CASE-004")
                .with_transaction(sample_transaction)
                .with_alert(sample_alert)
                .build()
            )

    def test_blank_case_id_raises_value_error(self):
        with pytest.raises(ValueError):
            FraudCaseBuilder("   ")

    def test_escalated_defaults_to_false(
        self, sample_transaction, sample_alert, sample_risk_score_critical
    ):
        case = (
            FraudCaseBuilder("CASE-005")
            .with_transaction(sample_transaction)
            .with_alert(sample_alert)
            .with_risk_score(sample_risk_score_critical)
            .build()
        )
        assert case.escalated is False

    def test_escalate_sets_flag(
        self, sample_transaction, sample_alert, sample_risk_score_critical
    ):
        case = (
            FraudCaseBuilder("CASE-006")
            .with_transaction(sample_transaction)
            .with_alert(sample_alert)
            .with_risk_score(sample_risk_score_critical)
            .escalate()
            .build()
        )
        assert case.escalated is True

    def test_critical_risk_auto_derives_priority_1(
        self, sample_transaction, sample_alert, sample_risk_score_critical
    ):
        case = (
            FraudCaseBuilder("CASE-007")
            .with_transaction(sample_transaction)
            .with_alert(sample_alert)
            .with_risk_score(sample_risk_score_critical)
            .build()
        )
        assert case.priority == 1

    def test_low_risk_auto_derives_priority_5(
        self, sample_transaction, sample_alert, sample_risk_score_low
    ):
        case = (
            FraudCaseBuilder("CASE-008")
            .with_transaction(sample_transaction)
            .with_alert(sample_alert)
            .with_risk_score(sample_risk_score_low)
            .build()
        )
        assert case.priority == 5

    def test_manual_priority_override(
        self, sample_transaction, sample_alert, sample_risk_score_critical
    ):
        case = (
            FraudCaseBuilder("CASE-009")
            .with_transaction(sample_transaction)
            .with_alert(sample_alert)
            .with_risk_score(sample_risk_score_critical)
            .set_priority(2)
            .build()
        )
        assert case.priority == 2

    def test_priority_out_of_range_raises_value_error(self):
        with pytest.raises(ValueError):
            FraudCaseBuilder("CASE-010").set_priority(6)

    def test_audit_trail_accumulates_entries(
        self, sample_transaction, sample_alert, sample_risk_score_critical
    ):
        log1 = AuditLog("CASE_OPENED", "system", {})
        log2 = AuditLog("ANALYST_ASSIGNED", "j.mokoena", {"analyst": "J Mokoena"})
        case = (
            FraudCaseBuilder("CASE-011")
            .with_transaction(sample_transaction)
            .with_alert(sample_alert)
            .with_risk_score(sample_risk_score_critical)
            .add_audit_entry(log1)
            .add_audit_entry(log2)
            .build()
        )
        assert len(case.audit_trail) == 2

    def test_notes_are_stored(
        self, sample_transaction, sample_alert, sample_risk_score_critical
    ):
        case = (
            FraudCaseBuilder("CASE-012")
            .with_transaction(sample_transaction)
            .with_alert(sample_alert)
            .with_risk_score(sample_risk_score_critical)
            .with_notes("High-priority review requested by compliance team.")
            .build()
        )
        assert "compliance" in case.investigator_notes

    def test_with_transaction_rejects_non_transaction(
        self, sample_alert, sample_risk_score_critical
    ):
        with pytest.raises(TypeError):
            FraudCaseBuilder("CASE-013").with_transaction("not-a-transaction")

    def test_with_alert_rejects_non_alert(
        self, sample_transaction, sample_risk_score_critical
    ):
        with pytest.raises(TypeError):
            FraudCaseBuilder("CASE-014").with_alert({"type": "fake"})