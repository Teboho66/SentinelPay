"""
SentinelPay – Assignment 12
api/routes/ml_models.py

MLModel REST API endpoints.
"""

from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query

import sys
import os

for _p in ("../../Assignment10", "../../Assignment11", ".."):
    _abs = os.path.abspath(os.path.join(os.path.dirname(__file__), _p))
    if _abs not in sys.path:
        sys.path.insert(0, _abs)

from config.schemas import (
    RegisterModelRequest,
    EvaluateModelRequest,
    PromoteModelRequest,
    HotSwapRequest,
    MLModelResponse,
    EvaluateModelResponse,
    ErrorResponse,
)
from config.dependencies import get_ml_model_service
from mapping.ml_model_service import MLModelService

from services.exceptions import (
    EntityNotFoundError,
    DuplicateEntityError,
    BusinessRuleViolationError,
    InvalidStateTransitionError,
    PromotionGateFailedError,
)

router = APIRouter(prefix="/api/ml-models", tags=["ML Models"])


def _handle_service_errors(exc: Exception) -> HTTPException:
    if isinstance(exc, EntityNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, DuplicateEntityError):
        return HTTPException(status_code=409, detail=str(exc))
    if isinstance(exc, PromotionGateFailedError):
        return HTTPException(status_code=422, detail=str(exc))
    if isinstance(exc, (BusinessRuleViolationError, ValueError)):
        return HTTPException(status_code=422, detail=str(exc))
    if isinstance(exc, InvalidStateTransitionError):
        return HTTPException(status_code=409, detail=str(exc))
    return HTTPException(status_code=500, detail=f"Internal error: {exc}")


@router.post(
    "",
    response_model=MLModelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new ML model version",
    description=(
        "FR-13: Registers a new model version in TRAINING stage. "
        "model_name must be one of: XGBOOST, ISOLATION_FOREST, DISTILBERT. "
        "Model ID is auto-generated as '{model_name_lower}-{version}'."
    ),
    responses={
        201: {"description": "Model registered in TRAINING stage"},
        409: {
            "model": ErrorResponse,
            "description": "Model version already registered",
        },
        422: {"model": ErrorResponse, "description": "Invalid model name"},
    },
)
def register_model(
    body: RegisterModelRequest,
    service: MLModelService = Depends(get_ml_model_service),
):
    try:
        model = service.register_model(
            model_name=body.model_name,
            version=body.version,
            artifact_path=body.artifact_path,
            feature_schema_version=body.feature_schema_version,
        )
        return MLModelResponse.from_domain(model)
    except Exception as e:
        raise _handle_service_errors(e)


@router.get(
    "",
    response_model=List[MLModelResponse],
    summary="Get all registered ML models",
    description="Returns all model versions. Filter by stage or model_name using query parameters.",
)
def get_all_models(
    stage: str = Query(None, example="PRODUCTION"),
    model_name: str = Query(None, example="XGBOOST"),
    service: MLModelService = Depends(get_ml_model_service),
):
    try:
        if stage:
            models = service.get_by_stage(stage)
        elif model_name:
            models = service.get_by_model_name(model_name)
        else:
            models = service.get_all_models()
        return [MLModelResponse.from_domain(m) for m in models]
    except Exception as e:
        raise _handle_service_errors(e)


@router.get(
    "/production",
    response_model=List[MLModelResponse],
    summary="Get all PRODUCTION models",
    description=(
        "FR-14: Returns all models currently in PRODUCTION stage. "
        "Polled every 60 seconds by the Model Loader for hot-swap detection."
    ),
)
def get_production_models(
    service: MLModelService = Depends(get_ml_model_service),
):
    return [MLModelResponse.from_domain(m) for m in service.get_production_models()]


@router.get(
    "/{model_id}",
    response_model=MLModelResponse,
    summary="Get a model by ID",
    responses={404: {"model": ErrorResponse, "description": "Model not found"}},
)
def get_model(
    model_id: str,
    service: MLModelService = Depends(get_ml_model_service),
):
    try:
        return MLModelResponse.from_domain(service.get_model(model_id))
    except Exception as e:
        raise _handle_service_errors(e)


@router.post(
    "/{model_id}/evaluate",
    response_model=EvaluateModelResponse,
    summary="Record evaluation metrics for a model",
    description=(
        "FR-13: Records precision, recall, F1, and AUC-ROC from holdout-set evaluation. "
        "Returns meets_promotion_gate: true/false indicating readiness for PRODUCTION promotion. "
        "Gate: precision ≥ 0.85 AND recall ≥ 0.80 (BR-ML1)."
    ),
    responses={
        200: {
            "description": "Metrics recorded; meets_promotion_gate indicates readiness"
        },
        404: {"model": ErrorResponse, "description": "Model not found"},
        409: {
            "model": ErrorResponse,
            "description": "Model not in TRAINING or STAGING stage",
        },
    },
)
def evaluate_model(
    model_id: str,
    body: EvaluateModelRequest,
    service: MLModelService = Depends(get_ml_model_service),
):
    try:
        model, metrics, meets_gate = service.evaluate_model(
            model_id=model_id,
            precision=body.precision,
            recall=body.recall,
            f1_score=body.f1_score,
            auc_roc=body.auc_roc,
        )
        return EvaluateModelResponse(
            model=MLModelResponse.from_domain(model),
            meets_promotion_gate=meets_gate,
            precision=metrics.precision,
            recall=metrics.recall,
            f1_score=metrics.f1_score,
            auc_roc=metrics.auc_roc,
        )
    except Exception as e:
        raise _handle_service_errors(e)


@router.patch(
    "/{model_id}/promote",
    response_model=MLModelResponse,
    summary="Promote a model to the next lifecycle stage",
    description=(
        "FR-13: Advances the model through TRAINING → STAGING → PRODUCTION → ARCHIVED. "
        "Promoting to PRODUCTION enforces BR-ML1 (precision ≥ 0.85 AND recall ≥ 0.80). "
        "Existing PRODUCTION model of the same type is automatically ARCHIVED (FR-13)."
    ),
    responses={
        200: {"description": "Model promoted to target stage"},
        404: {"model": ErrorResponse, "description": "Model not found"},
        409: {"model": ErrorResponse, "description": "Invalid stage transition"},
        422: {"model": ErrorResponse, "description": "Promotion gate failed (BR-ML1)"},
    },
)
def promote_model(
    model_id: str,
    body: PromoteModelRequest,
    service: MLModelService = Depends(get_ml_model_service),
):
    try:
        model = service.promote_model(model_id, body.target_stage)
        return MLModelResponse.from_domain(model)
    except Exception as e:
        raise _handle_service_errors(e)


@router.patch(
    "/{model_id}/hot-swap",
    response_model=MLModelResponse,
    summary="Hot-swap model artifact in PRODUCTION",
    description=(
        "FR-14: Reloads the model artifact for a PRODUCTION model without service restart. "
        "Only callable on PRODUCTION-stage models."
    ),
    responses={
        200: {"description": "Artifact path updated; hot-swap complete"},
        404: {"model": ErrorResponse, "description": "Model not found"},
        409: {
            "model": ErrorResponse,
            "description": "Model must be in PRODUCTION stage",
        },
    },
)
def hot_swap(
    model_id: str,
    body: HotSwapRequest,
    service: MLModelService = Depends(get_ml_model_service),
):
    try:
        model = service.hot_swap_artifact(model_id, body.new_artifact_path)
        return MLModelResponse.from_domain(model)
    except Exception as e:
        raise _handle_service_errors(e)


@router.delete(
    "/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a model version",
    description="PRODUCTION models cannot be deleted. Promote a replacement first.",
    responses={
        404: {"model": ErrorResponse, "description": "Model not found"},
        422: {"model": ErrorResponse, "description": "Cannot delete PRODUCTION model"},
    },
)
def delete_model(
    model_id: str,
    service: MLModelService = Depends(get_ml_model_service),
):
    try:
        service.delete_model(model_id)
    except Exception as e:
        raise _handle_service_errors(e)
