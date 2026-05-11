"""
SentinelPay – Pattern 3: Abstract Factory
==========================================
Intent  : Provide an interface for creating families of related or dependent
          objects without specifying their concrete classes.

Domain use-case
---------------
SentinelPay sends notifications through multiple channels.  Two concrete
families exist today:
  • EmailNotificationFactory  → produces EmailNotification + EmailAlertSummary
  • SMSNotificationFactory    → produces SMSNotification  + SMSAlertSummary

Adding WhatsApp or Push support in future requires only a new factory — no
changes to the alert dispatcher that calls the factory.

Why Abstract Factory here?
  - Each communication channel is a *family*: an alert notification paired
    with a case-summary report, both formatted consistently for that channel.
    Abstract Factory guarantees the two products stay in sync.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from src.models import (
    FraudAlert,
    Notification,
    EmailNotification,
    SMSNotification,
)


# ── Abstract products ────────────────────────────────────────────────────────

class AlertSummary(ABC):
    """Second product in the family: a formatted case-summary for analysts."""

    @abstractmethod
    def render(self) -> str:
        ...


class EmailAlertSummary(AlertSummary):
    def __init__(self, alert: FraudAlert, recipient: str) -> None:
        self._alert = alert
        self._recipient = recipient

    def render(self) -> str:
        return (
            f"--- SentinelPay Alert Summary (EMAIL) ---\n"
            f"Alert ID   : {self._alert.id}\n"
            f"Type       : {self._alert.alert_type}\n"
            f"Severity   : {self._alert.severity.name}\n"
            f"Created    : {self._alert.created_at.isoformat()}\n"
            f"Recipient  : {self._recipient}\n"
            f"Description: {self._alert.description}\n"
            f"-----------------------------------------"
        )


class SMSAlertSummary(AlertSummary):
    def __init__(self, alert: FraudAlert, phone: str) -> None:
        self._alert = alert
        self._phone = phone

    def render(self) -> str:
        return (
            f"[SentinelPay] ALERT {self._alert.alert_type} "
            f"(sev={self._alert.severity.name}) "
            f"txn={self._alert.transaction_id[:8]}. "
            f"Reply STOP to opt out."
        )


# ── Abstract Factory ─────────────────────────────────────────────────────────

class NotificationFactory(ABC):
    """Abstract Factory declaring the two product-creation methods."""

    @abstractmethod
    def create_notification(
        self, alert: FraudAlert, recipient: str
    ) -> Notification:
        ...

    @abstractmethod
    def create_summary(
        self, alert: FraudAlert, recipient: str
    ) -> AlertSummary:
        ...

    def dispatch(self, alert: FraudAlert, recipient: str) -> dict:
        """
        Convenience: create both products and send the notification.
        Returns a dict with the send result and the rendered summary.
        """
        notification = self.create_notification(alert, recipient)
        summary = self.create_summary(alert, recipient)
        return {
            "send_result": notification.send(),
            "summary": summary.render(),
        }


# ── Concrete Factories ───────────────────────────────────────────────────────

class EmailNotificationFactory(NotificationFactory):
    """Produces email-channel products."""

    def create_notification(self, alert: FraudAlert, recipient: str) -> EmailNotification:
        subject = f"[SentinelPay] {alert.severity.name} Alert – {alert.alert_type}"
        body = (
            f"A fraud alert has been raised for transaction "
            f"{alert.transaction_id}.\n\n"
            f"Severity: {alert.severity.name}\n"
            f"Details : {alert.description}"
        )
        return EmailNotification(recipient, subject, body)

    def create_summary(self, alert: FraudAlert, recipient: str) -> EmailAlertSummary:
        return EmailAlertSummary(alert, recipient)


class SMSNotificationFactory(NotificationFactory):
    """Produces SMS-channel products."""

    def create_notification(self, alert: FraudAlert, recipient: str) -> SMSNotification:
        body = (
            f"SentinelPay ALERT: {alert.alert_type} on txn "
            f"{alert.transaction_id[:8]}. Sev: {alert.severity.name}."
        )
        return SMSNotification(recipient, alert.alert_type, body)

    def create_summary(self, alert: FraudAlert, recipient: str) -> SMSAlertSummary:
        return SMSAlertSummary(alert, recipient)


# ── Factory selector helper ──────────────────────────────────────────────────

def get_notification_factory(channel: str) -> NotificationFactory:
    """
    Helper: returns the correct concrete factory for a channel name.
    This is intentionally a simple function, not another factory class —
    the Abstract Factory pattern itself already handles the complexity.
    """
    factories: dict[str, NotificationFactory] = {
        "EMAIL": EmailNotificationFactory(),
        "SMS": SMSNotificationFactory(),
    }
    factory = factories.get(channel.upper())
    if factory is None:
        raise ValueError(f"No notification factory registered for channel '{channel}'.")
    return factory