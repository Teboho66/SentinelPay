"""
SentinelPay – Assignment 12
services/ml_model_service.py

MLModelService
===============
Encapsulates all business logic for MLModel lifecycle operations.
Uses MLModelRepository (A11) for persistence.

Business rules enforced:
  - BR-ML1 : Promotion to PRODUCTION requires precision ≥ 0.85 AND recall ≥ 0.80
  - FR-13  : Only one PRODUCTION model per ModelName at a time
             (old production auto-archived when new one promoted)
  - FR-14  : hot_swap() callable on PRODUCTION models without service restart
  - ModelStage lifecycle: TRAINING → STAGING → PRODUCTION → ARCHIVED
"""

from __future__ import annotations
import sys, os
for _p in ("../Assignment10", "../Assignment11"):
    _abs = os.path.abspath(os.path.join(os.path.dirname(__file__), _p))
    if _abs not in sys.path:
        sys.path.insert(0, _abs)

from typing import List, Optional

from src.models import (
    MLModel, ModelName, ModelStage, EvaluationMetrics,
)
from repositories.interfaces import MLModelRepository
from services.exceptions import (
    EntityNotFoundError, DuplicateEntityError,
    BusinessRuleViolationError, InvalidStateTransitionError,
    PromotionGateFailedError,
)

# Valid lifecycle stage progressions
_VALID_PROMOTIONS = {
    ModelStage.TRAINING:  {ModelStage.STAGING, ModelStage.REJECTED},
    ModelStage.STAGING:   {ModelStage.PRODUCTION, ModelStage.REJECTED},
    ModelStage.PRODUCTION:{ModelStage.ARCHIVED},
    ModelStage.ARCHIVED:  set(),
    ModelStage.REJECTED:  set(),
}


class MLModelService:
    """
    Service layer for MLModel lifecycle operations.
    Injected with an MLModelRepository — storage-backend agnostic.
    """

    def __init__(self, ml_model_repo: MLModelRepository) -> None:
        self._repo = ml_model_repo

    # ── Command operations ────────────────────────────────────────────────────

    def register_model(
        self,
        model_name: str,
        version: str,
        artifact_path: str,
        feature_schema_version: str,
    ) -> MLModel:
        """
        FR-13: Register a new model version in TRAINING stage.

        Business rules:
          - model_name must be a valid ModelName enum value
          - model_id = f"{model_name_lower}-{version}" must be unique
        """
        try:
            name_enum = ModelName[model_name.upper()]
        except KeyError:
            raise BusinessRuleViolationError(
                "FR-13",
                f"Unknown model name '{model_name}'. "
                f"Valid: {[m.name for m in ModelName]}"
            )

        model_id = f"{name_enum.value.lower().replace('_', '-')}-{version}"
        if self._repo.exists(model_id):
            raise DuplicateEntityError("MLModel", "model_id", model_id)

        model = MLModel(
            model_id=model_id,
            model_name=name_enum,
            version=version,
            artifact_path=artifact_path,
            feature_schema_version=feature_schema_version,
            stage=ModelStage.TRAINING,
        )
        self._repo.save(model)
        return model

    def evaluate_model(
        self,
        model_id: str,
        precision: float,
        recall: float,
        f1_score: float,
        auc_roc: float,
    ) -> tuple[MLModel, EvaluationMetrics, bool]:
        """
        FR-13: Record evaluation metrics for a model.
        Returns (model, metrics, meets_gate) so the caller knows whether
        to proceed with promotion.
        """
        model = self._get_or_404(model_id)

        if model.stage not in (ModelStage.TRAINING, ModelStage.STAGING):
            raise InvalidStateTransitionError(
                "MLModel", model.stage.value, "evaluate"
            )

        metrics = EvaluationMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            auc_roc=auc_roc,
        )

        # Store metrics on the model
        model._precision = precision
        model._recall = recall
        model._f1_score = f1_score
        model._auc_roc = auc_roc
        self._repo.save(model)

        return model, metrics, metrics.meets_promotion_gate()

    def promote_model(self, model_id: str, target_stage: str) -> MLModel:
        """
        FR-13/FR-14: Advance a model through the lifecycle stages.

        Business rules:
          - Stage transition must follow _VALID_PROMOTIONS graph
          - Promoting to PRODUCTION: BR-ML1 gate must pass
          - Promoting to PRODUCTION: existing PRODUCTION model is auto-archived (FR-13)
        """
        model = self._get_or_404(model_id)

        try:
            target_enum = ModelStage[target_stage.upper()]
        except KeyError:
            raise BusinessRuleViolationError(
                "FR-13",
                f"Unknown stage '{target_stage}'. Valid: {[s.name for s in ModelStage]}"
            )

        # Validate lifecycle transition
        allowed = _VALID_PROMOTIONS.get(model.stage, set())
        if target_enum not in allowed:
            raise InvalidStateTransitionError(
                "MLModel",
                model.stage.value,
                f"promote to {target_enum.value}"
            )

        # BR-ML1: promotion gate for PRODUCTION
        if target_enum == ModelStage.PRODUCTION:
            if not model.meets_promotion_gate():
                raise PromotionGateFailedError(
                    model_id, model.precision, model.recall
                )
            # FR-13: archive the existing PRODUCTION model of same name
            existing_prod = self._repo.find_by_name_and_stage(
                model.model_name, ModelStage.PRODUCTION
            )
            if existing_prod is not None:
                existing_prod.promote(ModelStage.ARCHIVED)
                self._repo.save(existing_prod)

        model.promote(target_enum)
        self._repo.save(model)
        return model

    def hot_swap_artifact(self, model_id: str, new_artifact_path: str) -> MLModel:
        """
        FR-14: Reload model artifact in PRODUCTION without service restart.
        Only callable on PRODUCTION-stage models.
        """
        model = self._get_or_404(model_id)

        if model.stage != ModelStage.PRODUCTION:
            raise InvalidStateTransitionError(
                "MLModel", model.stage.value, "hot_swap (only valid for PRODUCTION models)"
            )

        if not new_artifact_path.strip():
            raise BusinessRuleViolationError(
                "FR-14", "new_artifact_path cannot be blank."
            )

        model.hot_swap(new_artifact_path)
        self._repo.save(model)
        return model

    # ── Query operations ──────────────────────────────────────────────────────

    def get_model(self, model_id: str) -> MLModel:
        """Return a model by ID or raise EntityNotFoundError (→ 404)."""
        return self._get_or_404(model_id)

    def get_all_models(self) -> List[MLModel]:
        """Return all registered models."""
        return self._repo.find_all()

    def get_production_models(self) -> List[MLModel]:
        """FR-14: Return all PRODUCTION models (polled every 60s by Model Loader)."""
        return self._repo.find_production_models()

    def get_by_stage(self, stage: str) -> List[MLModel]:
        """Return all models in a given lifecycle stage."""
        try:
            stage_enum = ModelStage[stage.upper()]
        except KeyError:
            raise BusinessRuleViolationError(
                "FR-13",
                f"Unknown stage '{stage}'. Valid: {[s.name for s in ModelStage]}"
            )
        return self._repo.find_by_stage(stage_enum)

    def get_by_model_name(self, model_name: str) -> List[MLModel]:
        """Return all versions of a specific model type."""
        try:
            name_enum = ModelName[model_name.upper()]
        except KeyError:
            raise BusinessRuleViolationError(
                "FR-13",
                f"Unknown model name '{model_name}'. Valid: {[m.name for m in ModelName]}"
            )
        return self._repo.find_by_model_name(name_enum)

    def delete_model(self, model_id: str) -> None:
        """Remove a model. PRODUCTION models cannot be deleted."""
        model = self._get_or_404(model_id)
        if model.stage == ModelStage.PRODUCTION:
            raise BusinessRuleViolationError(
                "FR-14",
                "PRODUCTION models cannot be deleted. Promote a replacement first."
            )
        self._repo.delete(model_id)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _get_or_404(self, model_id: str) -> MLModel:
        model = self._repo.find_by_id(model_id)
        if model is None:
            raise EntityNotFoundError("MLModel", model_id)
        return model