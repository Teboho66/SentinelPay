"""
Tests – Factory Method (AlertGenerator hierarchy)
===================================================
Covers:
  - Each concrete generator produces the correct alert type
  - Severity is mapped correctly from risk score
  - generate() returns None when score is below threshold
  - generate() returns a FraudAlert when score meets threshold
"""

import pytest
from creational_patterns.factory_method import (
    VelocityAlertGenerator,
    GeolocationAlertGenerator,
    MLAlertGenerator,
)
from src.models import FraudAlert, AlertSeverity


TXN_ID = "TXN-TEST-001"


class TestVelocityAlertGenerator:

    def setup_method(self):
        self.generator = VelocityAlertGenerator()

    def test_returns_none_below_threshold(self):
        result = self.generator.generate(TXN_ID, risk_score=0.40)
        assert result is None

    def test_returns_alert_at_threshold(self):
        result = self.generator.generate(TXN_ID, risk_score=0.55)
        assert isinstance(result, FraudAlert)

    def test_alert_type_is_velocity_breach(self):
        alert = self.generator.generate(TXN_ID, risk_score=0.60)
        assert alert.alert_type == "VELOCITY_BREACH"

    def test_high_risk_score_produces_high_severity(self):
        alert = self.generator.generate(TXN_ID, risk_score=0.85)
        assert alert.severity == AlertSeverity.HIGH

    def test_moderate_risk_score_produces_warning_severity(self):
        alert = self.generator.generate(TXN_ID, risk_score=0.60)
        assert alert.severity == AlertSeverity.WARNING

    def test_alert_contains_risk_score_in_description(self):
        alert = self.generator.generate(TXN_ID, risk_score=0.72)
        assert "0.72" in alert.description

    def test_alert_transaction_id_matches(self):
        alert = self.generator.generate(TXN_ID, risk_score=0.65)
        assert alert.transaction_id == TXN_ID


class TestGeolocationAlertGenerator:

    def setup_method(self):
        self.generator = GeolocationAlertGenerator()

    def test_returns_none_below_threshold(self):
        assert self.generator.generate(TXN_ID, 0.50) is None

    def test_returns_alert_at_threshold(self):
        assert self.generator.generate(TXN_ID, 0.65) is not None

    def test_alert_type_is_geo_anomaly(self):
        alert = self.generator.generate(TXN_ID, 0.70)
        assert alert.alert_type == "GEO_ANOMALY"

    def test_critical_severity_at_high_score(self):
        alert = self.generator.generate(TXN_ID, 0.95)
        assert alert.severity == AlertSeverity.CRITICAL

    def test_high_severity_at_moderate_score(self):
        alert = self.generator.generate(TXN_ID, 0.75)
        assert alert.severity == AlertSeverity.HIGH


class TestMLAlertGenerator:

    def setup_method(self):
        self.generator = MLAlertGenerator()

    def test_returns_none_below_threshold(self):
        assert self.generator.generate(TXN_ID, 0.60) is None

    def test_returns_alert_at_threshold(self):
        assert self.generator.generate(TXN_ID, 0.70) is not None

    def test_alert_type_is_ml_flag(self):
        alert = self.generator.generate(TXN_ID, 0.75)
        assert alert.alert_type == "ML_FLAG"

    def test_ml_alert_always_critical(self):
        alert = self.generator.generate(TXN_ID, 0.80)
        assert alert.severity == AlertSeverity.CRITICAL

    def test_confidence_percentage_in_description(self):
        alert = self.generator.generate(TXN_ID, 0.85)
        assert "85.00%" in alert.description