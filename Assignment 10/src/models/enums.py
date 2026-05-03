"""
SentinelPay – Shared Enumerations
Centralises all status/type constants used across domain models.
"""

from enum import Enum, auto


class TransactionStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    FLAGGED = "FLAGGED"
    BLOCKED = "BLOCKED"
    REVERSED = "REVERSED"


class TransactionType(Enum):
    ONLINE = "ONLINE"
    ATM = "ATM"
    POS = "POS"
    WIRE_TRANSFER = "WIRE_TRANSFER"
    CRYPTO = "CRYPTO"


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertSeverity(Enum):
    INFO = 1
    WARNING = 2
    HIGH = 3
    CRITICAL = 4


class NotificationChannel(Enum):
    EMAIL = auto()
    SMS = auto()
    PUSH = auto()


class PaymentMethodType(Enum):
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    DIGITAL_WALLET = "DIGITAL_WALLET"