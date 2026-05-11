"""
SentinelPay – Pattern 1: Simple Factory
========================================
Intent  : Centralise object creation behind a single static method so callers
          never need to know which concrete class they're getting.

Domain use-case
---------------
A TransactionFactory creates the correct concrete Transaction sub-type based on
a string channel identifier.  The three sub-types differ in default metadata and
validation logic relevant to each channel (Online, ATM, POS).

Why Simple Factory here?
  - Transaction creation is triggered in many places (API controllers, Kafka
    consumers, batch importers).  Centralising it means changing validation
    logic in one place rather than hunting through call-sites.
"""

from __future__ import annotations
from src.models import Transaction, TransactionType


# ── Concrete sub-types ───────────────────────────────────────────────────────

class OnlineTransaction(Transaction):
    """Transaction originating from a web/mobile channel."""

    def __init__(self, amount: float, currency: str, merchant_id: str, account_id: str) -> None:
        super().__init__(amount, currency, TransactionType.ONLINE, merchant_id, account_id)
        self.add_metadata("channel", "ONLINE")
        self.add_metadata("requires_3ds", True)


class ATMTransaction(Transaction):
    """Cash withdrawal or deposit at an ATM."""

    def __init__(self, amount: float, currency: str, merchant_id: str, account_id: str) -> None:
        super().__init__(amount, currency, TransactionType.ATM, merchant_id, account_id)
        self.add_metadata("channel", "ATM")
        self.add_metadata("physical_card_required", True)

    def is_high_value(self, threshold: float = 5_000.0) -> bool:
        # ATM withdrawals are flagged at a lower threshold
        return self._amount > threshold


class POSTransaction(Transaction):
    """In-store point-of-sale transaction."""

    def __init__(self, amount: float, currency: str, merchant_id: str, account_id: str) -> None:
        super().__init__(amount, currency, TransactionType.POS, merchant_id, account_id)
        self.add_metadata("channel", "POS")
        self.add_metadata("contactless_eligible", amount <= 500.0)


class WireTransferTransaction(Transaction):
    """International wire transfer."""

    def __init__(self, amount: float, currency: str, merchant_id: str, account_id: str) -> None:
        super().__init__(amount, currency, TransactionType.WIRE_TRANSFER, merchant_id, account_id)
        self.add_metadata("channel", "WIRE")
        self.add_metadata("cross_border", True)


# ── Simple Factory ───────────────────────────────────────────────────────────

class TransactionFactory:
    """
    Simple Factory: one static method, one responsibility.
    Callers pass a channel string; the factory decides which class to instantiate.
    """

    _REGISTRY: dict[str, type] = {
        "ONLINE": OnlineTransaction,
        "ATM": ATMTransaction,
        "POS": POSTransaction,
        "WIRE": WireTransferTransaction,
    }

    @staticmethod
    def create(
        channel: str,
        amount: float,
        currency: str,
        merchant_id: str,
        account_id: str,
    ) -> Transaction:
        """
        Create and return the correct Transaction sub-type.

        Parameters
        ----------
        channel     : One of "ONLINE", "ATM", "POS", "WIRE"
        amount      : Transaction amount (must be >= 0)
        currency    : ISO-4217 code, e.g. "ZAR"
        merchant_id : ID of the receiving merchant
        account_id  : ID of the originating account

        Raises
        ------
        ValueError  : If channel is not registered.
        """
        channel_upper = channel.upper()
        cls = TransactionFactory._REGISTRY.get(channel_upper)
        if cls is None:
            supported = ", ".join(TransactionFactory._REGISTRY)
            raise ValueError(
                f"Unknown channel '{channel}'. Supported channels: {supported}"
            )
        return cls(amount, currency, merchant_id, account_id)

    @staticmethod
    def supported_channels() -> list[str]:
        return list(TransactionFactory._REGISTRY.keys())