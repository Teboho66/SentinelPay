"""
Tests – MLModelService
========================
Unit tests for all business logic in MLModelService.
"""

import pytest
from repositories.inmemory import InMemoryMLModelRepository
from services import (
    MLModelService,
    EntityNotFoundError,
    DuplicateEntityError,
    BusinessRuleViolationError,
    InvalidStateTransitionError,
    PromotionGateFailedError,
)
from src.models import ModelStage


@pytest.fixture
def repo():
    return InMemoryMLModelRepository()


@pytest.fixture
def service(repo):
    return MLModelService(repo)


def register(service, name="XGBOOST", version="3.1"):
    return service.register_model(
        model_name=name,
        version=version,
        artifact_path=f"mlflow://models/{name.lower()}/{version}",
        feature_schema_version="tabular-v3",
    )


def register_and_pass_gate(service, name="XGBOOST", version="3.1"):
    """Register, evaluate with passing metrics, return model."""
    model = register(service, name, version)
    model, metrics, gate = service.evaluate_model(
        model.model_id, precision=0.91, recall=0.87, f1_score=0.89, auc_roc=0.94
    )
    return model


class TestRegisterModel:
    def test_registers_in_training_stage(self, service):
        model = register(service)
        assert model.stage == ModelStage.TRAINING

    def test_model_id_auto_generated(self, service):
        model = register(service, "XGBOOST", "3.1")
        assert model.model_id == "xgboost-3.1"

    def test_duplicate_model_id_raises_409(self, service):
        register(service)
        with pytest.raises(DuplicateEntityError):
            register(service)

    def test_unknown_model_name_raises_422(self, service):
        with pytest.raises(BusinessRuleViolationError, match="FR-13"):
            service.register_model("RANDOM_FOREST", "1.0", "mlflow://rf/1.0", "v1")

    def test_model_persisted_in_repo(self, service, repo):
        register(service)
        assert repo.exists("xgboost-3.1")


class TestEvaluateModel:
    def test_evaluate_records_metrics(self, service):
        model = register(service)
        model, metrics, gate = service.evaluate_model(
            model.model_id, 0.91, 0.87, 0.89, 0.94
        )
        assert model.precision == pytest.approx(0.91)
        assert model.recall == pytest.approx(0.87)

    def test_gate_passes_when_both_thresholds_met(self, service):
        model = register(service)
        _, _, gate = service.evaluate_model(model.model_id, 0.85, 0.80, 0.82, 0.90)
        assert gate is True

    def test_gate_fails_when_precision_below_threshold(self, service):
        model = register(service)
        _, _, gate = service.evaluate_model(model.model_id, 0.84, 0.85, 0.84, 0.90)
        assert gate is False

    def test_gate_fails_when_recall_below_threshold(self, service):
        model = register(service)
        _, _, gate = service.evaluate_model(model.model_id, 0.90, 0.79, 0.84, 0.91)
        assert gate is False

    def test_evaluate_nonexistent_raises_404(self, service):
        with pytest.raises(EntityNotFoundError):
            service.evaluate_model("MISSING", 0.90, 0.85, 0.87, 0.92)


class TestPromoteModel:
    def test_training_to_staging(self, service):
        model = register(service)
        model = service.promote_model(model.model_id, "STAGING")
        assert model.stage == ModelStage.STAGING

    def test_staging_to_production_passes_gate(self, service):
        model = register_and_pass_gate(service)
        model = service.promote_model(model.model_id, "STAGING")
        model = service.promote_model(model.model_id, "PRODUCTION")
        assert model.stage == ModelStage.PRODUCTION

    def test_production_promotion_fails_gate(self, service):
        model = register(service)
        # Low recall — fails gate
        service.evaluate_model(model.model_id, 0.91, 0.70, 0.79, 0.88)
        service.promote_model(model.model_id, "STAGING")
        with pytest.raises(PromotionGateFailedError):
            service.promote_model(model.model_id, "PRODUCTION")

    def test_existing_production_archived_on_new_promotion(self, service):
        # v1 reaches PRODUCTION
        m1 = register_and_pass_gate(service, version="3.1")
        service.promote_model(m1.model_id, "STAGING")
        service.promote_model(m1.model_id, "PRODUCTION")
        # v2 reaches PRODUCTION — v1 should be auto-archived
        m2 = register_and_pass_gate(service, version="3.2")
        service.promote_model(m2.model_id, "STAGING")
        service.promote_model(m2.model_id, "PRODUCTION")
        m1_refreshed = service.get_model(m1.model_id)
        assert m1_refreshed.stage == ModelStage.ARCHIVED

    def test_invalid_stage_transition_raises_409(self, service):
        model = register(service)
        with pytest.raises(InvalidStateTransitionError):
            service.promote_model(model.model_id, "PRODUCTION")  # must go via STAGING

    def test_unknown_target_stage_raises_422(self, service):
        model = register(service)
        with pytest.raises(BusinessRuleViolationError):
            service.promote_model(model.model_id, "LIVE")

    def test_promote_nonexistent_raises_404(self, service):
        with pytest.raises(EntityNotFoundError):
            service.promote_model("MISSING", "STAGING")


class TestHotSwap:
    def test_hot_swap_updates_artifact_path(self, service):
        model = register_and_pass_gate(service)
        service.promote_model(model.model_id, "STAGING")
        service.promote_model(model.model_id, "PRODUCTION")
        updated = service.hot_swap_artifact(model.model_id, "mlflow://xgb/3.1-hotfix")
        assert updated.artifact_path == "mlflow://xgb/3.1-hotfix"

    def test_hot_swap_on_non_production_raises_409(self, service):
        model = register(service)
        with pytest.raises(InvalidStateTransitionError):
            service.hot_swap_artifact(model.model_id, "mlflow://new/path")

    def test_hot_swap_blank_path_raises_422(self, service):
        model = register_and_pass_gate(service)
        service.promote_model(model.model_id, "STAGING")
        service.promote_model(model.model_id, "PRODUCTION")
        with pytest.raises(BusinessRuleViolationError, match="FR-14"):
            service.hot_swap_artifact(model.model_id, "   ")


class TestQueryOperations:
    def test_get_production_models(self, service):
        m = register_and_pass_gate(service)
        service.promote_model(m.model_id, "STAGING")
        service.promote_model(m.model_id, "PRODUCTION")
        prod = service.get_production_models()
        assert len(prod) == 1
        assert prod[0].stage == ModelStage.PRODUCTION

    def test_get_by_stage(self, service):
        m = register(service)
        service.promote_model(m.model_id, "STAGING")
        staging = service.get_by_stage("STAGING")
        assert len(staging) == 1

    def test_delete_non_production_model(self, service):
        model = register(service)
        service.delete_model(model.model_id)
        with pytest.raises(EntityNotFoundError):
            service.get_model(model.model_id)

    def test_delete_production_raises_422(self, service):
        model = register_and_pass_gate(service)
        service.promote_model(model.model_id, "STAGING")
        service.promote_model(model.model_id, "PRODUCTION")
        with pytest.raises(BusinessRuleViolationError, match="FR-14"):
            service.delete_model(model.model_id)

    def test_get_by_model_name(self, service):
        register(service, "XGBOOST", "3.1")
        register(service, "XGBOOST", "3.2")
        register(service, "DISTILBERT", "1.4")
        results = service.get_by_model_name("XGBOOST")
        assert len(results) == 2
