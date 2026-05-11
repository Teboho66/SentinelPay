"""
SentinelPay – Pattern 5: Prototype
=====================================
Intent  : Specify the kinds of objects to create using a prototypical instance,
          and create new objects by copying (cloning) this prototype.

Domain use-case
---------------
SentinelPay ships with a library of pre-configured FraudRules.  Creating a
rule from scratch (parsing policy documents, loading thresholds from config)
is expensive.  FraudRuleCache stores one canonical instance of each rule type
and hands out clones on demand.  Consumers can tweak a clone's threshold
without affecting the canonical prototype.

Why Prototype here?
  - Fraud rules have expensive initialisation (policy lookups, threshold
    calibration).  Cloning is orders of magnitude faster than re-initialising.
  - Rules are often customised per-merchant; cloning the base rule and
    adjusting the threshold keeps the canonical rule untouched.
"""

from __future__ import annotations
import copy
from src.models import FraudRule


# ── Prototype Cache ──────────────────────────────────────────────────────────

class FraudRuleCache:
    """
    Stores canonical FraudRule prototypes and returns deep copies on request.

    Usage
    -----
    cache = FraudRuleCache()
    cache.load_defaults()
    rule = cache.get_clone("HIGH_VELOCITY")
    rule.set_threshold(25)   # merchant-specific override — prototype unchanged
    """

    def __init__(self) -> None:
        self._cache: dict[str, FraudRule] = {}

    # ── Populate ─────────────────────────────────────────────────────────────

    def register(self, rule: FraudRule) -> None:
        """Add a canonical prototype to the cache."""
        self._cache[rule.rule_id] = rule

    def load_defaults(self) -> None:
        """Pre-populate the cache with SentinelPay's built-in rule set."""
        defaults = [
            FraudRule(
                rule_id="HIGH_VELOCITY",
                name="High Transaction Velocity",
                threshold=10,           # more than 10 transactions in 5 min
                action="FLAG",
            ),
            FraudRule(
                rule_id="LARGE_AMOUNT",
                name="Unusually Large Amount",
                threshold=50_000.0,     # ZAR
                action="BLOCK",
            ),
            FraudRule(
                rule_id="GEO_MISMATCH",
                name="Geographic Mismatch",
                threshold=5_000.0,      # km between consecutive transactions
                action="FLAG",
            ),
            FraudRule(
                rule_id="NEW_MERCHANT",
                name="First Transaction With New Merchant",
                threshold=1.0,          # boolean-style: 1 = first visit
                action="REVIEW",
            ),
            FraudRule(
                rule_id="ODD_HOURS",
                name="Transaction During Odd Hours",
                threshold=3.0,          # 00:00–03:00
                action="FLAG",
            ),
        ]
        for rule in defaults:
            self.register(rule)

    # ── Clone ─────────────────────────────────────────────────────────────────

    def get_clone(self, rule_id: str) -> FraudRule:
        """
        Return a deep copy of the prototype identified by rule_id.

        Raises
        ------
        KeyError : If rule_id is not in the cache.
        """
        prototype = self._cache.get(rule_id)
        if prototype is None:
            raise KeyError(f"No rule prototype registered for id '{rule_id}'.")
        return prototype.clone()

    def list_rules(self) -> list[str]:
        return list(self._cache.keys())

    def __len__(self) -> int:
        return len(self._cache)