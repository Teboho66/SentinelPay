"""
SentinelPay – Supporting Domain Models
FraudAlert, RiskScore, AuditLog, FraudRule, PaymentMethod, Notification
"""

from __future__ import annotations
import copy
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional
from .enums import AlertSeverity, NotificationChannel, PaymentMethodType, RiskLevel


# ══════════════════════════════════════════════════════════════════════════════
# FraudAlert
# ══════════════════════════════════════════════════════════════════════════════

class FraudAlert:
    """
    Generated when a transaction breaches one or more fraud rules.
    Maps to the FraudAlert class in the A9 class diagram.
    """

    def __init__(
        self,
        transaction_id: str,
        alert_type: str,
        severity: AlertSeverity,
        description: str,
        alert_id: Optional[str] = None,
    ) -> None:
        self._id: str = alert_id or str(uuid.uuid4())
        self._transaction_id: str = transaction_id
        self._alert_type: str = alert_type
        self._severity: AlertSeverity = severity
        self._description: str = description
        self._created_at: datetime = datetime.utcnow()
        self._resolved: bool = False

    @property
    def id(self) -> str:
        return self._id

    @property
    def transaction_id(self) -> str:
        return self._transaction_id

    @property
    def alert_type(self) -> str:
        return self._alert_type

    @property
    def severity(self) -> AlertSeverity:
        return self._severity

    @property
    def description(self) -> str:
        return self._description

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def resolved(self) -> bool:
        return self._resolved

    def resolve(self) -> None:
        self._resolved = True

    def __repr__(self) -> str:
        return (
            f"FraudAlert(id={self._id[:8]}…, type={self._alert_type}, "
            f"severity={self._severity.name}, resolved={self._resolved})"
        )


# ══════════════════════════════════════════════════════════════════════════════
# RiskScore
# ══════════════════════════════════════════════════════════════════════════════

class RiskScore:
    """
    Value object that encapsulates the computed fraud-risk for a transaction.
    """

    def __init__(self, score: float, factors: list[str]) -> None:
        if not 0.0 <= score <= 1.0:
            raise ValueError("Score must be in [0.0, 1.0].")
        self._score: float = score
        self._factors: list[str] = list(factors)
        self._calculated_at: datetime = datetime.utcnow()

    @property
    def score(self) -> float:
        return self._score

    @property
    def factors(self) -> list[str]:
        return list(self._factors)

    @property
    def calculated_at(self) -> datetime:
        return self._calculated_at

    def risk_level(self) -> RiskLevel:
        if self._score < 0.3:
            return RiskLevel.LOW
        if self._score < 0.6:
            return RiskLevel.MEDIUM
        if self._score < 0.85:
            return RiskLevel.HIGH
        return RiskLevel.CRITICAL

    def __repr__(self) -> str:
        return f"RiskScore(score={self._score:.2f}, level={self.risk_level().value})"


# ══════════════════════════════════════════════════════════════════════════════
# AuditLog
# ══════════════════════════════════════════════════════════════════════════════

class AuditLog:
    """
    Immutable audit trail entry. Maps to the AuditLog class in the A9 diagram.
    """

    def __init__(
        self,
        action: str,
        actor: str,
        details: dict[str, Any],
        entry_id: Optional[str] = None,
    ) -> None:
        self._entry_id: str = entry_id or str(uuid.uuid4())
        self._action: str = action
        self._actor: str = actor
        self._details: dict = dict(details)
        self._timestamp: datetime = datetime.utcnow()

    @property
    def entry_id(self) -> str:
        return self._entry_id

    @property
    def action(self) -> str:
        return self._action

    @property
    def actor(self) -> str:
        return self._actor

    @property
    def details(self) -> dict:
        return dict(self._details)

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    def __repr__(self) -> str:
        return f"AuditLog(id={self._entry_id[:8]}…, action={self._action}, actor={self._actor})"


# ══════════════════════════════════════════════════════════════════════════════
# FraudRule  (supports Prototype pattern)
# ══════════════════════════════════════════════════════════════════════════════

class FraudRule:
    """
    A configurable rule evaluated against each transaction.
    Implements __copy__ and __deepcopy__ to support the Prototype pattern.
    """

    def __init__(
        self,
        rule_id: str,
        name: str,
        threshold: float,
        action: str,
        is_active: bool = True,
    ) -> None:
        self._rule_id: str = rule_id
        self._name: str = name
        self._threshold: float = threshold
        self._action: str = action
        self._is_active: bool = is_active

    # ── Getters ──────────────────────────────────────────────────────────────

    @property
    def rule_id(self) -> str:
        return self._rule_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def threshold(self) -> float:
        return self._threshold

    @property
    def action(self) -> str:
        return self._action

    @property
    def is_active(self) -> bool:
        return self._is_active

    # ── Prototype support ────────────────────────────────────────────────────

    def clone(self) -> FraudRule:
        """Return a deep copy of this rule (Prototype pattern)."""
        return copy.deepcopy(self)

    def deactivate(self) -> None:
        self._is_active = False

    def set_threshold(self, threshold: float) -> None:
        self._threshold = threshold

    def __repr__(self) -> str:
        return (
            f"FraudRule(id={self._rule_id}, name={self._name}, "
            f"threshold={self._threshold}, active={self._is_active})"
        )


# ══════════════════════════════════════════════════════════════════════════════
# PaymentMethod hierarchy
# ══════════════════════════════════════════════════════════════════════════════

class PaymentMethod(ABC):
    """Abstract base class for all payment instruments."""

    def __init__(self, method_type: PaymentMethodType, owner_id: str) -> None:
        self._method_type: PaymentMethodType = method_type
        self._owner_id: str = owner_id
        self._is_verified: bool = False

    @property
    def method_type(self) -> PaymentMethodType:
        return self._method_type

    @property
    def owner_id(self) -> str:
        return self._owner_id

    @property
    def is_verified(self) -> bool:
        return self._is_verified

    def verify(self) -> None:
        self._is_verified = True

    @abstractmethod
    def get_masked_identifier(self) -> str:
        ...


class CreditCard(PaymentMethod):
    def __init__(self, owner_id: str, card_number: str, expiry: str) -> None:
        super().__init__(PaymentMethodType.CREDIT_CARD, owner_id)
        self._card_number: str = card_number
        self._expiry: str = expiry

    def get_masked_identifier(self) -> str:
        return f"****-****-****-{self._card_number[-4:]}"

    def __repr__(self) -> str:
        return f"CreditCard(masked={self.get_masked_identifier()}, owner={self._owner_id})"


class DebitCard(PaymentMethod):
    def __init__(self, owner_id: str, card_number: str, bank_code: str) -> None:
        super().__init__(PaymentMethodType.DEBIT_CARD, owner_id)
        self._card_number: str = card_number
        self._bank_code: str = bank_code

    def get_masked_identifier(self) -> str:
        return f"****-****-****-{self._card_number[-4:]}"

    def __repr__(self) -> str:
        return f"DebitCard(masked={self.get_masked_identifier()}, bank={self._bank_code})"


class DigitalWallet(PaymentMethod):
    def __init__(self, owner_id: str, wallet_address: str, provider: str) -> None:
        super().__init__(PaymentMethodType.DIGITAL_WALLET, owner_id)
        self._wallet_address: str = wallet_address
        self._provider: str = provider

    def get_masked_identifier(self) -> str:
        return f"{self._provider}:{self._wallet_address[:6]}…"

    def __repr__(self) -> str:
        return f"DigitalWallet(provider={self._provider}, owner={self._owner_id})"


# ══════════════════════════════════════════════════════════════════════════════
# Notification hierarchy
# ══════════════════════════════════════════════════════════════════════════════

class Notification(ABC):
    """Abstract notification – supports the Abstract Factory pattern."""

    def __init__(self, recipient: str, subject: str, body: str) -> None:
        self._recipient: str = recipient
        self._subject: str = subject
        self._body: str = body
        self._sent: bool = False

    @property
    def recipient(self) -> str:
        return self._recipient

    @property
    def subject(self) -> str:
        return self._subject

    @property
    def body(self) -> str:
        return self._body

    @property
    def sent(self) -> bool:
        return self._sent

    @abstractmethod
    def send(self) -> str:
        ...


class EmailNotification(Notification):
    def __init__(self, recipient_email: str, subject: str, body: str) -> None:
        super().__init__(recipient_email, subject, body)
        self._channel = NotificationChannel.EMAIL

    def send(self) -> str:
        self._sent = True
        return f"[EMAIL] To: {self._recipient} | Subject: {self._subject}"

    def __repr__(self) -> str:
        return f"EmailNotification(to={self._recipient}, sent={self._sent})"


class SMSNotification(Notification):
    def __init__(self, phone_number: str, subject: str, body: str) -> None:
        super().__init__(phone_number, subject, body)
        self._channel = NotificationChannel.SMS

    def send(self) -> str:
        self._sent = True
        return f"[SMS] To: {self._recipient} | {self._body[:60]}"

    def __repr__(self) -> str:
        return f"SMSNotification(to={self._recipient}, sent={self._sent})"