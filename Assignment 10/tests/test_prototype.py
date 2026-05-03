"""
Tests – Prototype (FraudRuleCache)
=====================================
Covers:
  - get_clone() returns a FraudRule, not the original
  - Cloned rule shares same field values as prototype
  - Mutating a clone does NOT affect the prototype
  - KeyError raised for unknown rule_id
  - load_defaults() registers 5 canonical rules
  - Custom rules can be registered and cloned
  - FraudRule.clone() produces a deep copy
"""

import pytest
from creational_patterns.prototype import FraudRuleCache
from src.models import FraudRule


class TestFraudRuleCache:

    def setup_method(self):
        self.cache = FraudRuleCache()
        self.cache.load_defaults()

    def test_load_defaults_registers_five_rules(self):
        assert len(self.cache) == 5

    def test_list_rules_contains_expected_ids(self):
        rules = self.cache.list_rules()
        assert "HIGH_VELOCITY" in rules
        assert "LARGE_AMOUNT" in rules
        assert "GEO_MISMATCH" in rules

    def test_get_clone_returns_fraud_rule(self):
        clone = self.cache.get_clone("HIGH_VELOCITY")
        assert isinstance(clone, FraudRule)

    def test_clone_is_not_the_same_object_as_prototype(self):
        clone1 = self.cache.get_clone("HIGH_VELOCITY")
        clone2 = self.cache.get_clone("HIGH_VELOCITY")
        assert clone1 is not clone2

    def test_clone_has_same_rule_id(self):
        clone = self.cache.get_clone("LARGE_AMOUNT")
        assert clone.rule_id == "LARGE_AMOUNT"

    def test_clone_has_same_threshold(self):
        clone = self.cache.get_clone("LARGE_AMOUNT")
        assert clone.threshold == pytest.approx(50_000.0)

    def test_clone_has_same_name(self):
        clone = self.cache.get_clone("GEO_MISMATCH")
        assert clone.name == "Geographic Mismatch"

    def test_mutating_clone_does_not_affect_prototype(self):
        original_threshold = self.cache.get_clone("HIGH_VELOCITY").threshold
        clone = self.cache.get_clone("HIGH_VELOCITY")
        clone.set_threshold(999)
        # Fetch fresh clone to confirm prototype is unchanged
        fresh_clone = self.cache.get_clone("HIGH_VELOCITY")
        assert fresh_clone.threshold == pytest.approx(original_threshold)

    def test_deactivating_clone_does_not_affect_prototype(self):
        clone = self.cache.get_clone("NEW_MERCHANT")
        clone.deactivate()
        assert clone.is_active is False
        # Original in cache should still be active
        fresh = self.cache.get_clone("NEW_MERCHANT")
        assert fresh.is_active is True

    def test_unknown_rule_id_raises_key_error(self):
        with pytest.raises(KeyError, match="UNKNOWN_RULE"):
            self.cache.get_clone("UNKNOWN_RULE")

    def test_custom_rule_can_be_registered_and_cloned(self):
        custom = FraudRule(
            rule_id="CUSTOM_RULE",
            name="Custom Merchant Rule",
            threshold=1_500.0,
            action="FLAG",
        )
        self.cache.register(custom)
        clone = self.cache.get_clone("CUSTOM_RULE")
        assert clone.threshold == pytest.approx(1_500.0)

    def test_fraud_rule_clone_method_deep_copies(self):
        rule = FraudRule("R-01", "Test Rule", 100.0, "FLAG")
        clone = rule.clone()
        clone.set_threshold(999.0)
        assert rule.threshold == pytest.approx(100.0)
        assert clone.threshold == pytest.approx(999.0)