"""
SentinelPay – Pattern 2: Factory Method
=========================================
Intent  : Define an interface for creating an object, but let sub-classes decide
          which class to instantiate.  Factory Method lets a class defer
          instantiation to sub-classes.

Domain use-case
---------------
SentinelPay must generate FraudAlerts of different types depending on the
detection strategy that triggers them.  The AlertGenerator abstract class
declares the factory method `create_alert()`.  Concrete sub-classes
(VelocityAlertGenerator, GeolocationAlertGenerator, MLAlertGenerator) each
know how to produce the right alert for their specialised detection logic.

Why Factory Method here?
  - New detection engines will be added over time.  Each engine only needs to
    sub-class AlertGenerator and implement `create_alert()` — the pipeline
    code that calls `generate()` never changes.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from src.models import FraudAlert, AlertSeverity


# ── Creator (abstract) ───────────────────────────────────────────────────────

class AlertGenerator(ABC):
    """
    Abstract Creator.
    Implements the detection workflow; delegates FraudAlert construction
    to the factory method `create_alert()`.
    """

    def generate(self, transaction_id: str, risk_score: float) -> FraudAlert | None:
        """
        Template-method style: run detection, then create an alert if needed.
        Returns None when the transaction is clean for this engine.
        """
        if not self._should_alert(risk_score):
            return None
        alert = self.create_alert(transaction_id, risk_score)
        self._log(alert)
        return alert

    @abstractmethod
    def create_alert(self, transaction_id: str, risk_score: float) -> FraudAlert:
        """Factory Method — concrete sub-classes implement this."""
        ...

    @abstractmethod
    def _should_alert(self, risk_score: float) -> bool:
        ...

    def _log(self, alert: FraudAlert) -> None:
        print(f"[AlertGenerator] Created {alert!r}")


# ── Concrete Creators ────────────────────────────────────────────────────────

class VelocityAlertGenerator(AlertGenerator):
    """
    Triggers when a card is used many times in a short window
    (velocity / rapid-fire fraud pattern).
    """

    _THRESHOLD = 0.55

    def _should_alert(self, risk_score: float) -> bool:
        return risk_score >= self._THRESHOLD

    def create_alert(self, transaction_id: str, risk_score: float) -> FraudAlert:
        severity = AlertSeverity.HIGH if risk_score >= 0.8 else AlertSeverity.WARNING
        return FraudAlert(
            transaction_id=transaction_id,
            alert_type="VELOCITY_BREACH",
            severity=severity,
            description=(
                f"Transaction velocity threshold exceeded. "
                f"Risk score: {risk_score:.2f}"
            ),
        )


class GeolocationAlertGenerator(AlertGenerator):
    """
    Triggers when the transaction originates from an unexpected geographic region.
    """

    _THRESHOLD = 0.65

    def _should_alert(self, risk_score: float) -> bool:
        return risk_score >= self._THRESHOLD

    def create_alert(self, transaction_id: str, risk_score: float) -> FraudAlert:
        severity = AlertSeverity.CRITICAL if risk_score >= 0.9 else AlertSeverity.HIGH
        return FraudAlert(
            transaction_id=transaction_id,
            alert_type="GEO_ANOMALY",
            severity=severity,
            description=(
                f"Transaction from unexpected geolocation. "
                f"Risk score: {risk_score:.2f}"
            ),
        )


class MLAlertGenerator(AlertGenerator):
    """
    Triggers based on the output of the ML fraud-scoring model.
    Used for pattern-based fraud that rules alone cannot catch.
    """

    _THRESHOLD = 0.70

    def _should_alert(self, risk_score: float) -> bool:
        return risk_score >= self._THRESHOLD

    def create_alert(self, transaction_id: str, risk_score: float) -> FraudAlert:
        return FraudAlert(
            transaction_id=transaction_id,
            alert_type="ML_FLAG",
            severity=AlertSeverity.CRITICAL,
            description=(
                f"ML model flagged this transaction as likely fraudulent. "
                f"Confidence: {risk_score:.2%}"
            ),
        )