"""
Tests – Simple Factory (TransactionFactory)
============================================
Covers:
  - Correct concrete type returned per channel
  - Channel names are case-insensitive
  - ValueError raised for unknown channel
  - Negative amount rejected by the model
  - Metadata populated correctly per sub-type
"""

import pytest
from creational_patterns.simple_factory import (
    TransactionFactory,
    OnlineTransaction,
    ATMTransaction,
    POSTransaction,
    WireTransferTransaction,
)
from src.models import TransactionStatus, TransactionType


class TestTransactionFactory:

    def test_creates_online_transaction(self):
        txn = TransactionFactory.create("ONLINE", 500.0, "ZAR", "MER-01", "ACC-01")
        assert isinstance(txn, OnlineTransaction)

    def test_creates_atm_transaction(self):
        txn = TransactionFactory.create("ATM", 1000.0, "ZAR", "MER-02", "ACC-02")
        assert isinstance(txn, ATMTransaction)

    def test_creates_pos_transaction(self):
        txn = TransactionFactory.create("POS", 250.0, "ZAR", "MER-03", "ACC-03")
        assert isinstance(txn, POSTransaction)

    def test_creates_wire_transaction(self):
        txn = TransactionFactory.create("WIRE", 75_000.0, "ZAR", "MER-04", "ACC-04")
        assert isinstance(txn, WireTransferTransaction)

    def test_channel_name_is_case_insensitive(self):
        txn = TransactionFactory.create("online", 100.0, "ZAR", "MER-05", "ACC-05")
        assert isinstance(txn, OnlineTransaction)

    def test_raises_value_error_for_unknown_channel(self):
        with pytest.raises(ValueError, match="Unknown channel"):
            TransactionFactory.create("CRYPTO_ALGO", 100.0, "ZAR", "MER-06", "ACC-06")

    def test_default_status_is_pending(self):
        txn = TransactionFactory.create("POS", 50.0, "ZAR", "MER-07", "ACC-07")
        assert txn.status == TransactionStatus.PENDING

    def test_amount_is_stored_correctly(self):
        txn = TransactionFactory.create("ONLINE", 1234.56, "ZAR", "MER-08", "ACC-08")
        assert txn.amount == pytest.approx(1234.56)

    def test_currency_normalised_to_uppercase(self):
        txn = TransactionFactory.create("POS", 50.0, "zar", "MER-09", "ACC-09")
        assert txn.currency == "ZAR"

    def test_negative_amount_raises_error(self):
        with pytest.raises(ValueError):
            TransactionFactory.create("ONLINE", -100.0, "ZAR", "MER-10", "ACC-10")

    def test_invalid_currency_raises_error(self):
        with pytest.raises(ValueError):
            TransactionFactory.create("ONLINE", 100.0, "RAND", "MER-11", "ACC-11")

    def test_online_transaction_has_3ds_metadata(self):
        txn = TransactionFactory.create("ONLINE", 200.0, "ZAR", "MER-12", "ACC-12")
        assert txn.metadata.get("requires_3ds") is True

    def test_atm_transaction_has_high_value_threshold_override(self):
        # ATM overrides is_high_value() threshold to 5000
        txn = TransactionFactory.create("ATM", 6000.0, "ZAR", "MER-13", "ACC-13")
        assert txn.is_high_value() is True
        txn_low = TransactionFactory.create("ATM", 4000.0, "ZAR", "MER-14", "ACC-14")
        assert txn_low.is_high_value() is False

    def test_pos_contactless_eligible_below_500(self):
        txn = TransactionFactory.create("POS", 300.0, "ZAR", "MER-15", "ACC-15")
        assert txn.metadata.get("contactless_eligible") is True

    def test_pos_not_contactless_above_500(self):
        txn = TransactionFactory.create("POS", 700.0, "ZAR", "MER-16", "ACC-16")
        assert txn.metadata.get("contactless_eligible") is False

    def test_supported_channels_returns_all_four(self):
        channels = TransactionFactory.supported_channels()
        assert set(channels) == {"ONLINE", "ATM", "POS", "WIRE"}