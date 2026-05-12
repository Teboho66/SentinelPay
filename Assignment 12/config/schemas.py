"""
SentinelPay – Assignment 12
api/schemas.py

Pydantic request/response models for all three REST APIs.
These are completely decoupled from the domain entities — the API layer
translates between schemas and domain objects in the route handlers.
"""

from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# ══════════════════════════════════════════════════════════════════════════════
# Transaction Schemas
# ══════════════════════════════════════════════════════════════════════════════

class SubmitTransactionRequest(BaseModel):
    """POST /api/transactions — submit a new transaction for fraud evaluation."""
    transaction_id: str = Field(..., example="TXN-2026-001", description="Unique transaction identifier")
    account_id_token: str = Field(..., example="acc_token_abc123", description="Tokenised account identifier")
    merchant_id: str = Field(..., example="MER-001")
    merchant_category_code: str = Field(..., example="5411", description="ISO 18245 MCC")
    amount: Decimal = Field(..., gt=0, example=1500.00, description="Transaction amount (BR-T1: Decimal precision)")
    currency: str = Field(..., min_length=3, max_length=3, example="ZAR", description="ISO 4217 currency code")
    channel: str = Field(..., example="CNP_ONLINE", description="One of: CNP_ONLINE, CNP_MOBILE, POS, ATM")
    device_fingerprint_token: str = Field(..., example="dfp_token_xyz789")
    ip_address_hash: str = Field(..., example="a3f8bc912d")
    latitude: float = Field(..., ge=-90, le=90, example=-33.9249)
    longitude: float = Field(..., ge=-180, le=180, example=18.4241)
    is_international: bool = Field(False, example=False)

    @field_validator("currency")
    @classmethod
    def currency_uppercase(cls, v: str) -> str:
        return v.upper()


class ModelScoreInput(BaseModel):
    model_name: str = Field(..., example="XGBOOST")
    model_version: str = Field(..., example="3.1")
    raw_score: float = Field(..., ge=0.0, le=1.0, example=0.87)
    confidence: float = Field(..., ge=0.0, le=1.0, example=0.91)


class ApplyDecisionRequest(BaseModel):
    """POST /api/transactions/{id}/decision — apply ML ensemble scores and produce FraudDecision."""
    fraud_score: float = Field(..., ge=0.0, le=1.0, example=0.87)
    model_scores: List[ModelScoreInput] = Field(..., min_length=1)
    account_tier: str = Field("STANDARD", example="STANDARD", description="One of: STANDARD, PREMIUM, BUSINESS")


class TransactionResponse(BaseModel):
    """Response schema for Transaction — safe to return (no raw PII)."""
    transaction_id: str
    account_id_token: str
    merchant_id: str
    merchant_category_code: str
    amount: Decimal
    currency: str
    channel: str
    is_international: bool
    fraud_score: float
    risk_tier: str
    decision: Optional[str]
    model_version_composite: str
    processing_ms: int
    pii_tokenised: bool

    @classmethod
    def from_domain(cls, txn) -> "TransactionResponse":
        return cls(
            transaction_id=txn.transaction_id,
            account_id_token=txn.account_id_token,
            merchant_id=txn.merchant_id,
            merchant_category_code=txn.merchant_category_code,
            amount=txn.amount,
            currency=txn.currency,
            channel=txn.channel.value,
            is_international=txn.is_international,
            fraud_score=txn.fraud_score,
            risk_tier=txn.risk_tier.value,
            decision=txn.decision.value if txn.decision else None,
            model_version_composite=txn.model_version_composite,
            processing_ms=txn.processing_ms,
            pii_tokenised=txn.pii_tokenised,
        )

    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════════════════════════════
# FraudCase Schemas
# ══════════════════════════════════════════════════════════════════════════════

class CreateFraudCaseRequest(BaseModel):
    """POST /api/fraud-cases — create a fraud investigation case."""
    transaction_id: str = Field(..., example="TXN-2026-001")
    account_id_token: str = Field(..., example="acc_token_abc123")
    fraud_score: float = Field(..., ge=0.0, le=1.0, example=0.93)
    risk_tier: str = Field(..., example="CRITICAL", description="Must be HIGH or CRITICAL (FR-09)")
    shap_report_ref: str = Field("", example="s3://shap-reports/TXN-2026-001.json")


class AssignAnalystRequest(BaseModel):
    """PATCH /api/fraud-cases/{id}/assign — assign case to a fraud analyst."""
    analyst_id: str = Field(..., example="j.mokoena", description="Analyst employee ID")


class ResolveCaseRequest(BaseModel):
    """PATCH /api/fraud-cases/{id}/resolve — resolve a case."""
    resolution: str = Field(..., example="CONFIRMED", description="CONFIRMED or DISMISSED")
    note: str = Field("", example="Velocity fraud pattern confirmed via geo analysis.")


class FraudCaseResponse(BaseModel):
    """Response schema for FraudCase."""
    case_id: str
    transaction_id: str
    account_id_token: str
    fraud_score: float
    risk_tier: str
    priority: str
    status: str
    assigned_analyst_id: Optional[str]
    shap_report_ref: str
    analyst_note: str
    created_at: datetime
    resolved_at: Optional[datetime]
    sla_breach_at: datetime
    is_breaching_sla: bool

    @classmethod
    def from_domain(cls, case) -> "FraudCaseResponse":
        return cls(
            case_id=case.case_id,
            transaction_id=case.transaction_id,
            account_id_token=case.account_id_token,
            fraud_score=case.fraud_score,
            risk_tier=case.risk_tier.value,
            priority=case.priority.value,
            status=case.status.value,
            assigned_analyst_id=case.assigned_analyst_id,
            shap_report_ref=case.shap_report_ref,
            analyst_note=case.analyst_note,
            created_at=case.created_at,
            resolved_at=case.resolved_at,
            sla_breach_at=case.sla_breach_at,
            is_breaching_sla=case.is_breaching_sla(),
        )

    model_config = {"from_attributes": True}


class ResolveCaseResponse(BaseModel):
    case: FraudCaseResponse
    fraud_label_payload: Optional[dict] = None


# ══════════════════════════════════════════════════════════════════════════════
# MLModel Schemas
# ══════════════════════════════════════════════════════════════════════════════

class RegisterModelRequest(BaseModel):
    """POST /api/ml-models — register a new model version."""
    model_name: str = Field(..., example="XGBOOST", description="One of: XGBOOST, ISOLATION_FOREST, DISTILBERT")
    version: str = Field(..., example="3.2")
    artifact_path: str = Field(..., example="mlflow://models/xgboost/3.2")
    feature_schema_version: str = Field(..., example="tabular-v3")


class EvaluateModelRequest(BaseModel):
    """POST /api/ml-models/{id}/evaluate — record holdout-set evaluation metrics."""
    precision: float = Field(..., ge=0.0, le=1.0, example=0.91)
    recall: float = Field(..., ge=0.0, le=1.0, example=0.87)
    f1_score: float = Field(..., ge=0.0, le=1.0, example=0.89)
    auc_roc: float = Field(..., ge=0.0, le=1.0, example=0.94)


class PromoteModelRequest(BaseModel):
    """PATCH /api/ml-models/{id}/promote — advance model through lifecycle stages."""
    target_stage: str = Field(..., example="STAGING", description="One of: STAGING, PRODUCTION, ARCHIVED, REJECTED")


class HotSwapRequest(BaseModel):
    """PATCH /api/ml-models/{id}/hot-swap — reload artifact in PRODUCTION without restart."""
    new_artifact_path: str = Field(..., example="mlflow://models/xgboost/3.2-hotfix")


class MLModelResponse(BaseModel):
    """Response schema for MLModel."""
    model_id: str
    model_name: str
    version: str
    stage: str
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    artifact_path: str
    feature_schema_version: str
    meets_promotion_gate: bool
    trained_at: datetime
    promoted_at: Optional[datetime]

    @classmethod
    def from_domain(cls, model) -> "MLModelResponse":
        return cls(
            model_id=model.model_id,
            model_name=model.model_name.value,
            version=model.version,
            stage=model.stage.value,
            precision=model.precision,
            recall=model.recall,
            f1_score=model.f1_score,
            auc_roc=model.auc_roc,
            artifact_path=model.artifact_path,
            feature_schema_version=model.feature_schema_version,
            meets_promotion_gate=model.meets_promotion_gate(),
            trained_at=model.trained_at,
            promoted_at=model.promoted_at,
        )

    model_config = {"from_attributes": True}


class EvaluateModelResponse(BaseModel):
    model: MLModelResponse
    meets_promotion_gate: bool
    precision: float
    recall: float
    f1_score: float
    auc_roc: float


# ══════════════════════════════════════════════════════════════════════════════
# Common error schemas
# ══════════════════════════════════════════════════════════════════════════════

class ErrorResponse(BaseModel):
    error: str
    detail: str
    status_code: int