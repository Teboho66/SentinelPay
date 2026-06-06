"""
SentinelPay – Assignment 12
services/ml_model_service.py

MLModelService
===============
Encapsulates all business logic for MLModel lifecycle operations.
Uses MLModelRepository (A11) for persistence.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import List

for _p in ("../Assignment10", "../Assignment11"):
    _abs = os.path.abspath(os.path.join(os.path.dirname(__file__), _p))
    if _abs not in sys.path:
        sys.path.insert(0, _abs)

from src.models import (
    MLModel,
    ModelName,
    ModelStage,
    EvaluationMetrics,
)
from repositories.interfaces import MLModelRepository
from services.exceptions import (
    EntityNotFoundError,
    DuplicateEntityError,
    BusinessRuleViolationError,
    InvalidStateTransitionError,
    PromotionGateFailedError,
)


PROMOTION_PRECISION_THRESHOLD = 0.85
PROMOTION_RECALL_THRESHOLD = 0.80

_ALLOWED_MODEL_NAMES = {"XGBOOST", "LIGHTGBM", "NEURAL_NET", "DISTILBERT"}


def _value(value):
    return getattr(value, "value", value)


def _set_attr(obj, public_name: str, private_name: str, value) -> None:
    try:
        setattr(obj, public_name, value)
    except AttributeError:
        pass

    try:
        setattr(obj, private_name, value)
    except AttributeError:
        pass


def _stage_is(model, stage) -> bool:
    return _value(getattr(model, "stage", None)) == _value(stage)


def _name_is(model, name) -> bool:
    return _value(getattr(model, "model_name", None)) == _value(name)


def _meets_promotion_gate(model) -> bool:
    precision = getattr(model, "precision", 0.0) or 0.0
    recall = getattr(model, "recall", 0.0) or 0.0
    return (
        precision >= PROMOTION_PRECISION_THRESHOLD
        and recall >= PROMOTION_RECALL_THRESHOLD
    )


class MLModelService:
    def __init__(self, ml_model_repo: MLModelRepository) -> None:
        self._repo = ml_model_repo

    def register_model(
        self,
        model_name: str,
        version: str,
        artifact_path: str,
        feature_schema_version: str,
    ) -> MLModel:
        name_value = model_name.upper()

        if name_value not in _ALLOWED_MODEL_NAMES or not hasattr(ModelName, name_value):
            raise BusinessRuleViolationError(
                "FR-13",
                f"Unknown model name '{model_name}'.",
            )

        name_enum = getattr(ModelName, name_value)
        model_id = f"{_value(name_enum).lower().replace('_', '-')}-{version}"

        if self._repo.exists(model_id):
            raise DuplicateEntityError("MLModel", "model_id", model_id)

        model = MLModel(
            model_id=model_id,
            model_name=name_enum,
            version=version,
            artifact_uri=artifact_path,
            feature_set=feature_schema_version,
        )

        _set_attr(model, "model_id", "_model_id", model_id)
        _set_attr(model, "model_name", "_model_name", name_enum)
        _set_attr(model, "version", "_version", version)
        _set_attr(model, "stage", "_stage", ModelStage.TRAINING)

        _set_attr(model, "artifact_path", "_artifact_path", artifact_path)
        _set_attr(model, "artifact_uri", "_artifact_uri", artifact_path)
        _set_attr(
            model,
            "feature_schema_version",
            "_feature_schema_version",
            feature_schema_version,
        )
        _set_attr(model, "feature_set", "_feature_set", feature_schema_version)

        _set_attr(model, "precision", "_precision", None)
        _set_attr(model, "recall", "_recall", None)
        _set_attr(model, "f1_score", "_f1_score", None)
        _set_attr(model, "auc_roc", "_auc_roc", None)
        _set_attr(model, "trained_at", "_trained_at", datetime.utcnow())
        _set_attr(model, "promoted_at", "_promoted_at", None)

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
        model = self._get_or_404(model_id)

        if not _stage_is(model, ModelStage.TRAINING) and not _stage_is(
            model,
            ModelStage.STAGING,
        ):
            raise InvalidStateTransitionError(
                "MLModel",
                _value(model.stage),
                "evaluate",
            )

        metrics = EvaluationMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            auc_roc=auc_roc,
        )

        _set_attr(model, "precision", "_precision", precision)
        _set_attr(model, "recall", "_recall", recall)
        _set_attr(model, "f1_score", "_f1_score", f1_score)
        _set_attr(model, "auc_roc", "_auc_roc", auc_roc)

        gate = (
            precision >= PROMOTION_PRECISION_THRESHOLD
            and recall >= PROMOTION_RECALL_THRESHOLD
        )

        self._repo.save(model)
        return model, metrics, gate

    def promote_model(self, model_id: str, target_stage: str) -> MLModel:
        model = self._get_or_404(model_id)

        stage_value = target_stage.upper()

        if not hasattr(ModelStage, stage_value):
            raise BusinessRuleViolationError(
                "FR-13",
                f"Unknown stage '{target_stage}'.",
            )

        target_enum = getattr(ModelStage, stage_value)
        current_stage = _value(model.stage)
        target = _value(target_enum)

        if current_stage == target:
            raise InvalidStateTransitionError(
                "MLModel",
                current_stage,
                f"promote to {target}",
            )

        if current_stage == "TRAINING" and target == "STAGING":
            _set_attr(model, "stage", "_stage", target_enum)
            self._repo.save(model)
            return model

        if current_stage == "STAGING" and target == "PRODUCTION":
            if not _meets_promotion_gate(model):
                raise PromotionGateFailedError(
                    model_id,
                    getattr(model, "precision", 0.0) or 0.0,
                    getattr(model, "recall", 0.0) or 0.0,
                )

            for existing in self._repo.find_all():
                if (
                    existing.model_id != model.model_id
                    and _name_is(existing, model.model_name)
                    and _stage_is(existing, ModelStage.PRODUCTION)
                ):
                    _set_attr(existing, "stage", "_stage", ModelStage.ARCHIVED)
                    self._repo.save(existing)

            _set_attr(model, "stage", "_stage", ModelStage.PRODUCTION)
            _set_attr(model, "promoted_at", "_promoted_at", datetime.utcnow())
            self._repo.save(model)
            return model

        if current_stage == "PRODUCTION" and target == "ARCHIVED":
            _set_attr(model, "stage", "_stage", ModelStage.ARCHIVED)
            self._repo.save(model)
            return model

        if target == "REJECTED":
            _set_attr(model, "stage", "_stage", ModelStage.REJECTED)
            self._repo.save(model)
            return model

        raise InvalidStateTransitionError(
            "MLModel",
            current_stage,
            f"promote to {target}",
        )

    def hot_swap_artifact(self, model_id: str, new_artifact_path: str) -> MLModel:
        model = self._get_or_404(model_id)

        if not new_artifact_path.strip():
            raise BusinessRuleViolationError(
                "FR-14",
                "new_artifact_path cannot be blank.",
            )

        if not _stage_is(model, ModelStage.PRODUCTION):
            raise InvalidStateTransitionError(
                "MLModel",
                _value(model.stage),
                "hot_swap",
            )

        _set_attr(model, "artifact_path", "_artifact_path", new_artifact_path)
        _set_attr(model, "artifact_uri", "_artifact_uri", new_artifact_path)

        self._repo.save(model)
        return model

    def hot_swap_model(self, model_id: str, new_artifact_path: str) -> MLModel:
        return self.hot_swap_artifact(model_id, new_artifact_path)

    def hot_swap(self, model_id: str, new_artifact_path: str) -> MLModel:
        return self.hot_swap_artifact(model_id, new_artifact_path)

    def get_model(self, model_id: str) -> MLModel:
        return self._get_or_404(model_id)

    def get_all_models(self) -> List[MLModel]:
        return self._repo.find_all()

    def get_production_models(self) -> List[MLModel]:
        return [
            model
            for model in self._repo.find_all()
            if _stage_is(model, ModelStage.PRODUCTION)
        ]

    def get_by_stage(self, stage: str) -> List[MLModel]:
        stage_value = stage.upper()

        if not hasattr(ModelStage, stage_value):
            raise BusinessRuleViolationError(
                "FR-13",
                f"Unknown stage '{stage}'.",
            )

        stage_enum = getattr(ModelStage, stage_value)

        return [
            model
            for model in self._repo.find_all()
            if _stage_is(model, stage_enum)
        ]

    def get_by_model_name(self, model_name: str) -> List[MLModel]:
        name_value = model_name.upper()

        if name_value not in _ALLOWED_MODEL_NAMES or not hasattr(ModelName, name_value):
            raise BusinessRuleViolationError(
                "FR-13",
                f"Unknown model name '{model_name}'.",
            )

        name_enum = getattr(ModelName, name_value)

        return [
            model
            for model in self._repo.find_all()
            if _name_is(model, name_enum)
        ]

    def delete_model(self, model_id: str) -> None:
        model = self._get_or_404(model_id)

        if _stage_is(model, ModelStage.PRODUCTION):
            raise BusinessRuleViolationError(
                "FR-14",
                "PRODUCTION models cannot be deleted.",
            )

        self._repo.delete(model_id)

    def _get_or_404(self, model_id: str) -> MLModel:
        model = self._repo.find_by_id(model_id)
        if model is None:
            raise EntityNotFoundError("MLModel", model_id)
        return model