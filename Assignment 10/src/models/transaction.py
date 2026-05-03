"""
SentinelPay – Transaction Model
Represents a financial transaction flowing through the fraud-detection pipeline.
"""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from .enums import TransactionStatus, TransactionType


class Transaction:
    """
    Core domain entity.  Maps directly to the Transaction class in the A9
    class diagram, which carried:
      id, amount, currency, timestamp, status, transactionType,
      merchantId, accountId, riskScore, flagged
    """

    def __init__(
        self,
        amount: float,
        currency: str,
        transaction_type: TransactionType,
        merchant_id: str,
        account_id: str,
        transaction_id: Optional[str] = None,
    ) -> None:
        if amount < 0:
            raise ValueError("Transaction amount cannot be negative.")
        if not currency or len(currency) != 3:
            raise ValueError("Currency must be a 3-character ISO code (e.g. 'ZAR').")

        self._id: str = transaction_id or str(uuid.uuid4())
        self._amount: float = amount
        self._currency: str = currency.upper()
        self._transaction_type: TransactionType = transaction_type
        self._merchant_id: str = merchant_id
        self._account_id: str = account_id
        self._timestamp: datetime = datetime.utcnow()
        self._status: TransactionStatus = TransactionStatus.PENDING
        self._risk_score: float = 0.0
        self._flagged: bool = False
        self._metadata: dict = {}

    # ── Getters ──────────────────────────────────────────────────────────────

    @property
    def id(self) -> str:
        return self._id

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def transaction_type(self) -> TransactionType:
        return self._transaction_type

    @property
    def merchant_id(self) -> str:
        return self._merchant_id

    @property
    def account_id(self) -> str:
        return self._account_id

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def status(self) -> TransactionStatus:
        return self._status

    @property
    def risk_score(self) -> float:
        return self._risk_score

    @property
    def flagged(self) -> bool:
        return self._flagged

    @property
    def metadata(self) -> dict:
        return dict(self._metadata)

    # ── Setters / mutators ───────────────────────────────────────────────────

    def update_status(self, new_status: TransactionStatus) -> None:
        self._status = new_status

    def set_risk_score(self, score: float) -> None:
        if not 0.0 <= score <= 1.0:
            raise ValueError("Risk score must be between 0.0 and 1.0.")
        self._risk_score = score
        self._flagged = score >= 0.7

    def add_metadata(self, key: str, value: object) -> None:
        self._metadata[key] = value

    # ── Business logic ───────────────────────────────────────────────────────

    def is_high_value(self, threshold: float = 10_000.0) -> bool:
        return self._amount > threshold

    def approve(self) -> None:
        self._status = TransactionStatus.APPROVED

    def block(self) -> None:
        self._status = TransactionStatus.BLOCKED

    def __repr__(self) -> str:
        return (
            f"Transaction(id={self._id[:8]}…, amount={self._currency} {self._amount:.2f}, "
            f"type={self._transaction_type.value}, status={self._status.value})"
        )