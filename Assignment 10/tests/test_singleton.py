"""
Tests – Singleton (AuditLogger)
==================================
Covers:
  - get_instance() returns the same object every time
  - Direct construction raises RuntimeError
  - log() appends an AuditLog entry
  - get_logs() returns a copy (not the internal list)
  - filter_by_action() returns correct subset
  - Thread safety: concurrent writes from 50 threads all recorded
  - copy / deepcopy raise RuntimeError (Singleton cannot be cloned)
  - _reset() enables test isolation
"""

import copy
import threading
import pytest
from creational_patterns.singleton import AuditLogger


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the Singleton before and after every test for isolation."""
    AuditLogger._reset()
    yield
    AuditLogger._reset()


class TestAuditLoggerSingleton:

    def test_get_instance_returns_audit_logger(self):
        logger = AuditLogger.get_instance()
        assert isinstance(logger, AuditLogger)

    def test_same_instance_returned_on_repeated_calls(self):
        a = AuditLogger.get_instance()
        b = AuditLogger.get_instance()
        assert a is b

    def test_direct_construction_raises_runtime_error(self):
        AuditLogger.get_instance()          # create instance first
        with pytest.raises(RuntimeError, match="Singleton"):
            AuditLogger()

    def test_log_increases_entry_count(self):
        logger = AuditLogger.get_instance()
        assert logger.entry_count == 0
        logger.log("TRANSACTION_APPROVED", actor="system", details={"txn": "TXN-001"})
        assert logger.entry_count == 1

    def test_get_logs_returns_list(self):
        logger = AuditLogger.get_instance()
        logger.log("CASE_OPENED", actor="analyst")
        logs = logger.get_logs()
        assert len(logs) == 1

    def test_get_logs_returns_copy_not_reference(self):
        logger = AuditLogger.get_instance()
        logger.log("CASE_OPENED", actor="analyst")
        logs = logger.get_logs()
        logs.clear()
        assert logger.entry_count == 1    # internal list unaffected

    def test_log_entry_has_correct_action(self):
        logger = AuditLogger.get_instance()
        entry = logger.log("FRAUD_BLOCKED", actor="rule_engine")
        assert entry.action == "FRAUD_BLOCKED"

    def test_log_entry_has_correct_actor(self):
        logger = AuditLogger.get_instance()
        entry = logger.log("CASE_ESCALATED", actor="j.mokoena")
        assert entry.actor == "j.mokoena"

    def test_filter_by_action_returns_matching_entries(self):
        logger = AuditLogger.get_instance()
        logger.log("APPROVED", actor="system")
        logger.log("BLOCKED", actor="system")
        logger.log("APPROVED", actor="analyst")
        approved = logger.filter_by_action("APPROVED")
        assert len(approved) == 2

    def test_filter_by_action_returns_empty_for_no_match(self):
        logger = AuditLogger.get_instance()
        logger.log("APPROVED", actor="system")
        result = logger.filter_by_action("NONEXISTENT_ACTION")
        assert result == []

    def test_copy_raises_runtime_error(self):
        logger = AuditLogger.get_instance()
        with pytest.raises(RuntimeError, match="cannot be copied"):
            copy.copy(logger)

    def test_deepcopy_raises_runtime_error(self):
        logger = AuditLogger.get_instance()
        with pytest.raises(RuntimeError, match="cannot be deep-copied"):
            copy.deepcopy(logger)

    def test_thread_safety_concurrent_writes(self):
        """
        Spawn 50 threads, each writing 10 log entries.
        Expected total = 500 entries with no data races.
        """
        logger = AuditLogger.get_instance()
        barrier = threading.Barrier(50)

        def write_logs():
            barrier.wait()              # all threads start simultaneously
            for i in range(10):
                logger.log("CONCURRENT_TEST", actor="thread", details={"i": i})

        threads = [threading.Thread(target=write_logs) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert logger.entry_count == 500

    def test_clear_resets_log(self):
        logger = AuditLogger.get_instance()
        logger.log("EVENT", actor="system")
        logger.clear()
        assert logger.entry_count == 0