"""
SentinelPay – Assignment 12
api/routes/fraud_cases.py

FraudCase REST API endpoints.
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
    CreateFraudCaseRequest,
    AssignAnalystRequest,
    ResolveCaseRequest,
    FraudCaseResponse,
    ResolveCaseResponse,
    ErrorResponse,
)
from config.dependencies import get_fraud_case_service
from mapping.fraud_case_service import FraudCaseService
from api.metrics import fraud_cases_total

from services.exceptions import (
    EntityNotFoundError,
    DuplicateEntityError,
    BusinessRuleViolationError,
    InvalidStateTransitionError,
)

router = APIRouter(prefix="/api/fraud-cases", tags=["Fraud Cases"])


def _handle_service_errors(exc: Exception) -> HTTPException:
    if isinstance(exc, EntityNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, DuplicateEntityError):
        return HTTPException(status_code=409, detail=str(exc))
    if isinstance(exc, (BusinessRuleViolationError, ValueError)):
        return HTTPException(status_code=422, detail=str(exc))
    if isinstance(exc, InvalidStateTransitionError):
        return HTTPException(status_code=409, detail=str(exc))
    return HTTPException(status_code=500, detail=f"Internal error: {exc}")


@router.post(
    "",
    response_model=FraudCaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a fraud investigation case",
    description=(
        "FR-09: Creates a fraud case for a HARD_BLOCK transaction with HIGH or CRITICAL "
        "risk tier. Priority is automatically derived: P1 (≥0.90), P2 (≥0.75), P3 (<0.75). "
        "Enforces one case per transaction_id."
    ),
    responses={
        201: {"description": "Case created and added to analyst queue"},
        409: {
            "model": ErrorResponse,
            "description": "Case already exists for this transaction",
        },
        422: {
            "model": ErrorResponse,
            "description": "Risk tier must be HIGH or CRITICAL (FR-09)",
        },
    },
)
def create_fraud_case(
    body: CreateFraudCaseRequest,
    service: FraudCaseService = Depends(get_fraud_case_service),
):
    try:
        case = service.create_case(
            transaction_id=body.transaction_id,
            account_id_token=body.account_id_token,
            fraud_score=body.fraud_score,
            risk_tier=body.risk_tier,
            shap_report_ref=body.shap_report_ref,
        )
        # ── Increment metrics ──
        fraud_cases_total.inc()
        
        return FraudCaseResponse.from_domain(case)
    except Exception as e:
        raise _handle_service_errors(e)


@router.get(
    "",
    response_model=List[FraudCaseResponse],
    summary="Get all fraud cases",
    description="Returns all fraud cases. Filter by status or priority using query parameters.",
)
def get_all_cases(
    status: str = Query(None, example="OPEN"),
    priority: str = Query(None, example="P1"),
    service: FraudCaseService = Depends(get_fraud_case_service),
):
    try:
        if status:
            cases = service.get_by_status(status)
        elif priority:
            cases = service.get_by_priority(priority)
        else:
            cases = service.get_all_cases()
        return [FraudCaseResponse.from_domain(c) for c in cases]
    except Exception as e:
        raise _handle_service_errors(e)


@router.get(
    "/queue",
    response_model=List[FraudCaseResponse],
    summary="Get analyst case queue",
    description=(
        "FR-10: Returns all OPEN and IN_REVIEW cases sorted by priority (P1 first). "
        "SLA breach status is included in each case response."
    ),
)
def get_analyst_queue(
    service: FraudCaseService = Depends(get_fraud_case_service),
):
    cases = service.get_analyst_queue()
    return [FraudCaseResponse.from_domain(c) for c in cases]


@router.get(
    "/{case_id}",
    response_model=FraudCaseResponse,
    summary="Get a fraud case by ID",
    responses={404: {"model": ErrorResponse, "description": "Case not found"}},
)
def get_case(
    case_id: str,
    service: FraudCaseService = Depends(get_fraud_case_service),
):
    try:
        return FraudCaseResponse.from_domain(service.get_case(case_id))
    except Exception as e:
        raise _handle_service_errors(e)


@router.patch(
    "/{case_id}/assign",
    response_model=FraudCaseResponse,
    summary="Assign a case to a fraud analyst",
    description=(
        "FR-10: Assigns an OPEN case to a named analyst. "
        "Moves case status from OPEN → IN_REVIEW."
    ),
    responses={
        200: {"description": "Case assigned to analyst"},
        404: {"model": ErrorResponse, "description": "Case not found"},
        409: {"model": ErrorResponse, "description": "Case is not in OPEN state"},
    },
)
def assign_to_analyst(
    case_id: str,
    body: AssignAnalystRequest,
    service: FraudCaseService = Depends(get_fraud_case_service),
):
    try:
        case = service.assign_to_analyst(case_id, body.analyst_id)
        return FraudCaseResponse.from_domain(case)
    except Exception as e:
        raise _handle_service_errors(e)


@router.patch(
    "/{case_id}/resolve",
    response_model=ResolveCaseResponse,
    summary="Resolve a fraud case",
    description=(
        "FR-10: Resolves a case as CONFIRMED or DISMISSED. "
        "CONFIRMED publishes a fraud label to the MLOps retraining pipeline (BR-FC3). "
        "DISMISSED requires a non-empty analyst note (BR-FC2)."
    ),
    responses={
        200: {"description": "Case resolved; fraud_label_payload present if CONFIRMED"},
        404: {"model": ErrorResponse, "description": "Case not found"},
        409: {
            "model": ErrorResponse,
            "description": "Case must be IN_REVIEW to resolve",
        },
        422: {
            "model": ErrorResponse,
            "description": "DISMISSED requires a note (BR-FC2)",
        },
    },
)
def resolve_case(
    case_id: str,
    body: ResolveCaseRequest,
    service: FraudCaseService = Depends(get_fraud_case_service),
):
    try:
        case, label_payload = service.resolve_case(case_id, body.resolution, body.note)
        return ResolveCaseResponse(
            case=FraudCaseResponse.from_domain(case),
            fraud_label_payload=label_payload,
        )
    except Exception as e:
        raise _handle_service_errors(e)


@router.delete(
    "/{case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a fraud case",
    description="CONFIRMED cases cannot be deleted — they feed the retraining pipeline.",
    responses={
        404: {"model": ErrorResponse, "description": "Case not found"},
        422: {
            "model": ErrorResponse,
            "description": "CONFIRMED cases cannot be deleted",
        },
    },
)
def delete_case(
    case_id: str,
    service: FraudCaseService = Depends(get_fraud_case_service),
):
    try:
        service.delete_case(case_id)
    except Exception as e:
        raise _handle_service_errors(e)
