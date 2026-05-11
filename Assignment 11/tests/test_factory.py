"""
Tests – RepositoryFactory
===========================
Verifies that the factory correctly resolves implementations per entity
and storage type, and raises appropriate errors for invalid inputs.
"""

import pytest
from factories.repository_factory import RepositoryFactory
from repositories.inmemory import (
    InMemoryTransactionRepository,
    InMemoryFraudCaseRepository,
    InMemoryMLModelRepository,
    InMemoryAuditRecordRepository,
    InMemoryAccountProfileRepository,
    InMemoryCustomerDisputeRepository,
    InMemoryStepUpChallengeRepository,
)


class TestRepositoryFactory:

    def test_get_transaction_repo_memory(self):
        repo = RepositoryFactory.get("Transaction", "MEMORY")
        assert isinstance(repo, InMemoryTransactionRepository)

    def test_get_fraud_case_repo_memory(self):
        repo = RepositoryFactory.get("FraudCase", "MEMORY")
        assert isinstance(repo, InMemoryFraudCaseRepository)

    def test_get_ml_model_repo_memory(self):
        repo = RepositoryFactory.get("MLModel", "MEMORY")
        assert isinstance(repo, InMemoryMLModelRepository)

    def test_get_audit_record_repo_memory(self):
        repo = RepositoryFactory.get("AuditRecord", "MEMORY")
        assert isinstance(repo, InMemoryAuditRecordRepository)

    def test_get_account_profile_repo_memory(self):
        repo = RepositoryFactory.get("AccountProfile", "MEMORY")
        assert isinstance(repo, InMemoryAccountProfileRepository)

    def test_get_customer_dispute_repo_memory(self):
        repo = RepositoryFactory.get("CustomerDispute", "MEMORY")
        assert isinstance(repo, InMemoryCustomerDisputeRepository)

    def test_get_step_up_challenge_repo_memory(self):
        repo = RepositoryFactory.get("StepUpChallenge", "MEMORY")
        assert isinstance(repo, InMemoryStepUpChallengeRepository)

    def test_entity_name_is_case_insensitive(self):
        repo = RepositoryFactory.get("transaction", "MEMORY")
        assert isinstance(repo, InMemoryTransactionRepository)

    def test_storage_type_is_case_insensitive(self):
        repo = RepositoryFactory.get("Transaction", "memory")
        assert isinstance(repo, InMemoryTransactionRepository)

    def test_unknown_entity_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown entity"):
            RepositoryFactory.get("BookRepository", "MEMORY")

    def test_unknown_storage_type_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown storage type"):
            RepositoryFactory.get("Transaction", "ORACLE")

    def test_factory_returns_new_instance_each_call(self):
        repo1 = RepositoryFactory.get("Transaction", "MEMORY")
        repo2 = RepositoryFactory.get("Transaction", "MEMORY")
        assert repo1 is not repo2

    def test_typed_helpers_return_correct_types(self):
        assert isinstance(RepositoryFactory.get_transaction_repo(), InMemoryTransactionRepository)
        assert isinstance(RepositoryFactory.get_fraud_case_repo(), InMemoryFraudCaseRepository)
        assert isinstance(RepositoryFactory.get_ml_model_repo(), InMemoryMLModelRepository)
        assert isinstance(RepositoryFactory.get_audit_record_repo(), InMemoryAuditRecordRepository)
        assert isinstance(RepositoryFactory.get_account_profile_repo(), InMemoryAccountProfileRepository)
        assert isinstance(RepositoryFactory.get_customer_dispute_repo(), InMemoryCustomerDisputeRepository)
        assert isinstance(RepositoryFactory.get_step_up_challenge_repo(), InMemoryStepUpChallengeRepository)

    def test_filesystem_stub_returns_stub_instance(self):
        from stubs.filesystem_repository import FileSystemRepositoryStub
        repo = RepositoryFactory.get("Transaction", "FILESYSTEM")
        assert isinstance(repo, FileSystemRepositoryStub)

    def test_database_stub_returns_stub_instance(self):
        from stubs.database_repository import DatabaseRepositoryStub
        repo = RepositoryFactory.get("Transaction", "DATABASE")
        assert isinstance(repo, DatabaseRepositoryStub)