"""
SentinelPay – Pattern 4: Builder
==================================
Intent  : Separate the construction of a complex object from its representation
          so that the same construction process can create different representations.

Domain use-case
---------------
FraudCase is a complex aggregate: it bundles a suspicious Transaction, the
FraudAlert it generated, the RiskScore computed, optional AuditLog entries,
investigator notes, and an escalation flag.  Not every case will have all fields.

The FraudCaseBuilder lets the caller set only what it needs via a fluent API,
then calls `.build()` to get a fully validated FraudCase object.

Why Builder here?
  - FraudCase has 7+ fields, most optional.  Passing them all through a
    constructor would require 2^7 overloads or a mess of keyword arguments
    with unclear defaults.  Builder makes intent explicit at each call-site.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from src.models import (
    Transaction,
    FraudAlert,
    RiskScore,
    AuditLog,
    RiskLevel,
)


# ── Product ──────────────────────────────────────────────────────────────────

@dataclass
class FraudCase:
    """
    Aggregate built by FraudCaseBuilder.
    Not intended to be constructed directly.
    """
    case_id: str
    transaction: Transaction
    alert: FraudAlert
    risk_score: RiskScore
    audit_trail: list[AuditLog] = field(default_factory=list)
    investigator_notes: str = ""
    escalated: bool = False
    priority: int = 3          # 1 = Critical … 5 = Low

    def summarise(self) -> str:
        return (
            f"FraudCase [{self.case_id}]\n"
            f"  Transaction : {self.transaction!r}\n"
            f"  Alert       : {self.alert!r}\n"
            f"  Risk Score  : {self.risk_score!r}\n"
            f"  Priority    : {self.priority}\n"
            f"  Escalated   : {self.escalated}\n"
            f"  Audit Logs  : {len(self.audit_trail)} entries\n"
            f"  Notes       : {self.investigator_notes or '(none)'}"
        )


# ── Builder ──────────────────────────────────────────────────────────────────

class FraudCaseBuilder:
    """
    Fluent Builder for FraudCase.

    Example
    -------
    case = (
        FraudCaseBuilder("CASE-001")
        .with_transaction(txn)
        .with_alert(alert)
        .with_risk_score(score)
        .with_notes("Investigated by analyst J. Mokoena")
        .escalate()
        .build()
    )
    """

    def __init__(self, case_id: str) -> None:
        if not case_id.strip():
            raise ValueError("case_id cannot be blank.")
        self._case_id: str = case_id
        self._transaction: Optional[Transaction] = None
        self._alert: Optional[FraudAlert] = None
        self._risk_score: Optional[RiskScore] = None
        self._audit_trail: list[AuditLog] = []
        self._investigator_notes: str = ""
        self._escalated: bool = False
        self._priority: int = 3

    def with_transaction(self, transaction: Transaction) -> FraudCaseBuilder:
        if not isinstance(transaction, Transaction):
            raise TypeError("Expected a Transaction instance.")
        self._transaction = transaction
        return self

    def with_alert(self, alert: FraudAlert) -> FraudCaseBuilder:
        if not isinstance(alert, FraudAlert):
            raise TypeError("Expected a FraudAlert instance.")
        self._alert = alert
        return self

    def with_risk_score(self, risk_score: RiskScore) -> FraudCaseBuilder:
        if not isinstance(risk_score, RiskScore):
            raise TypeError("Expected a RiskScore instance.")
        self._risk_score = risk_score
        # Auto-derive priority from risk level
        self._priority = {
            RiskLevel.LOW: 5,
            RiskLevel.MEDIUM: 4,
            RiskLevel.HIGH: 2,
            RiskLevel.CRITICAL: 1,
        }[risk_score.risk_level()]
        return self

    def add_audit_entry(self, log: AuditLog) -> FraudCaseBuilder:
        self._audit_trail.append(log)
        return self

    def with_notes(self, notes: str) -> FraudCaseBuilder:
        self._investigator_notes = notes.strip()
        return self

    def escalate(self) -> FraudCaseBuilder:
        self._escalated = True
        return self

    def set_priority(self, priority: int) -> FraudCaseBuilder:
        if not 1 <= priority <= 5:
            raise ValueError("Priority must be an integer 1–5.")
        self._priority = priority
        return self

    def build(self) -> FraudCase:
        """
        Validate and construct the FraudCase.

        Raises
        ------
        ValueError : If any required field (transaction, alert, risk_score)
                     has not been set.
        """
        missing = [
            name for name, val in [
                ("transaction", self._transaction),
                ("alert", self._alert),
                ("risk_score", self._risk_score),
            ] if val is None
        ]
        if missing:
            raise ValueError(
                f"Cannot build FraudCase — missing required field(s): {', '.join(missing)}"
            )

        return FraudCase(
            case_id=self._case_id,
            transaction=self._transaction,
            alert=self._alert,
            risk_score=self._risk_score,
            audit_trail=list(self._audit_trail),
            investigator_notes=self._investigator_notes,
            escalated=self._escalated,
            priority=self._priority,
        )