"""
SentinelPay – Assignment 12
handlers/routes/transactions.py
handlers/routes/fraud_cases.py
handlers/routes/ml_models.py

Transaction REST API endpoints.
All business logic lives in TransactionService — routes only handle
HTTP concerns (serialisation, status codes, error mapping).
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
    SubmitTransactionRequest,
    ApplyDecisionRequest,
    TransactionResponse,
    ErrorResponse,
)

from config.dependencies import get_transaction_service
from mapping.transaction_service import TransactionService
from api.metrics import transactions_total, fraud_decisions_total

from services.exceptions import (
    EntityNotFoundError,
    DuplicateEntityError,
    BusinessRuleViolationError,
    InvalidStateTransitionError,
)

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


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
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a transaction for fraud evaluation",
    description=(
        "Accepts a transaction from the Payment Processor, validates the schema (FR-02), "
        "tokenises PII (BR-T2), and persists the transaction ready for ML scoring."
    ),
    responses={
        201: {"description": "Transaction accepted and persisted"},
        409: {"model": ErrorResponse, "description": "Duplicate transaction_id"},
        422: {
            "model": ErrorResponse,
            "description": "Schema validation failed (FR-02)",
        },
    },
)
def submit_transaction(
    body: SubmitTransactionRequest,
    service: TransactionService = Depends(get_transaction_service),
):
    try:
        txn = service.submit_transaction(
            transaction_id=body.transaction_id,
            account_id_token=body.account_id_token,
            merchant_id=body.merchant_id,
            merchant_category_code=body.merchant_category_code,
            amount=body.amount,
            currency=body.currency,
            channel=body.channel,
            device_fingerprint_token=body.device_fingerprint_token,
            ip_address_hash=body.ip_address_hash,
            latitude=body.latitude,
            longitude=body.longitude,
            is_international=body.is_international,
        )
        # ── Increment metrics ──
        transactions_total.labels(channel=body.channel).inc()
        fraud_decisions_total.labels(decision_type=txn.fraud_decision.value).inc()
        
        return TransactionResponse.from_domain(txn)
    except Exception as e:
        raise _handle_service_errors(e)


@router.get(
    "",
    response_model=List[TransactionResponse],
    summary="Fetch all transactions",
    description="Returns all persisted transactions. Supports optional filtering by decision or risk_tier.",
)
def get_all_transactions(
    decision: str = Query(
        None, example="HARD_BLOCK", description="Filter by FraudDecision"
    ),
    risk_tier: str = Query(None, example="CRITICAL", description="Filter by RiskTier"),
    service: TransactionService = Depends(get_transaction_service),
):
    try:
        if decision:
            txns = service.get_by_decision(decision)
        elif risk_tier:
            txns = service.get_by_risk_tier(risk_tier)
        else:
            txns = service.get_all_transactions()
        return [TransactionResponse.from_domain(t) for t in txns]
    except Exception as e:
        raise _handle_service_errors(e)


@router.get(
    "/flagged",
    response_model=List[TransactionResponse],
    summary="Get all HARD_BLOCK transactions",
    description="FR-09: Returns all HARD_BLOCK transactions for the fraud case generation pipeline.",
)
def get_flagged_transactions(
    service: TransactionService = Depends(get_transaction_service),
):
    return [
        TransactionResponse.from_domain(t) for t in service.get_flagged_transactions()
    ]


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get a transaction by ID",
    responses={404: {"model": ErrorResponse, "description": "Transaction not found"}},
)
def get_transaction(
    transaction_id: str,
    service: TransactionService = Depends(get_transaction_service),
):
    try:
        return TransactionResponse.from_domain(service.get_transaction(transaction_id))
    except Exception as e:
        raise _handle_service_errors(e)


@router.post(
    "/{transaction_id}/decision",
    response_model=TransactionResponse,
    summary="Apply fraud decision to a transaction",
    description=(
        "FR-07: Applies ML ensemble model scores, computes the composite fraud_score, "
        "and produces a FraudDecision (APPROVE / SOFT_DECLINE / HARD_BLOCK) using "
        "per-account-tier thresholds."
    ),
    responses={
        200: {"description": "Decision applied successfully"},
        404: {"model": ErrorResponse, "description": "Transaction not found"},
        409: {"model": ErrorResponse, "description": "Decision already applied"},
        422: {"model": ErrorResponse, "description": "Invalid model scores"},
    },
)
def apply_decision(
    transaction_id: str,
    body: ApplyDecisionRequest,
    service: TransactionService = Depends(get_transaction_service),
):
    try:
        txn = service.apply_fraud_decision(
            transaction_id=transaction_id,
            fraud_score=body.fraud_score,
            model_scores=[s.model_dump() for s in body.model_scores],
            account_tier=body.account_tier,
        )
        return TransactionResponse.from_domain(txn)
    except Exception as e:
        raise _handle_service_errors(e)


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a transaction",
    responses={404: {"model": ErrorResponse, "description": "Transaction not found"}},
)
def delete_transaction(
    transaction_id: str,
    service: TransactionService = Depends(get_transaction_service),
):
    try:
        service.delete_transaction(transaction_id)
    except Exception as e:
        raise _handle_service_errors(e)
