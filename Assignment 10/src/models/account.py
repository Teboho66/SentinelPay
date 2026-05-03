"""
SentinelPay – Account Model
Represents a customer account subject to fraud monitoring.
"""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from .enums import RiskLevel


class Account:
    """
    Maps to the Account entity in the A9 class diagram:
      id, holderName, email, phone, riskLevel, isActive,
      transactionHistory, createdAt
    """

    def __init__(
        self,
        holder_name: str,
        email: str,
        phone: str,
        account_id: Optional[str] = None,
    ) -> None:
        if not holder_name.strip():
            raise ValueError("Holder name cannot be blank.")
        if "@" not in email:
            raise ValueError("Invalid email address.")

        self._id: str = account_id or str(uuid.uuid4())
        self._holder_name: str = holder_name.strip()
        self._email: str = email.lower().strip()
        self._phone: str = phone.strip()
        self._risk_level: RiskLevel = RiskLevel.LOW
        self._is_active: bool = True
        self._created_at: datetime = datetime.utcnow()
        self._transaction_ids: list[str] = []

    # ── Getters ──────────────────────────────────────────────────────────────

    @property
    def id(self) -> str:
        return self._id

    @property
    def holder_name(self) -> str:
        return self._holder_name

    @property
    def email(self) -> str:
        return self._email

    @property
    def phone(self) -> str:
        return self._phone

    @property
    def risk_level(self) -> RiskLevel:
        return self._risk_level

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def transaction_ids(self) -> list[str]:
        return list(self._transaction_ids)

    # ── Mutators ─────────────────────────────────────────────────────────────

    def update_risk_level(self, level: RiskLevel) -> None:
        self._risk_level = level

    def deactivate(self) -> None:
        self._is_active = False

    def activate(self) -> None:
        self._is_active = True

    def link_transaction(self, transaction_id: str) -> None:
        if transaction_id not in self._transaction_ids:
            self._transaction_ids.append(transaction_id)

    def __repr__(self) -> str:
        return (
            f"Account(id={self._id[:8]}…, holder={self._holder_name}, "
            f"risk={self._risk_level.value}, active={self._is_active})"
        )