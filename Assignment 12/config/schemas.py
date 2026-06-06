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

def enum_value(value):
    return getattr(value, "value", value)


# ══════════════════════════════════════════════════════════════════════════════
# Transaction Schemas
# ══════════════════════════════════════════════════════════════════════════════


class SubmitTransactionRequest(BaseModel):
    """POST /api/transactions — submit a new transaction for fraud evaluation."""

    transaction_id: str = Field(
        ..., example="TXN-2026-001", description="Unique transaction identifier"
    )
    account_id_token: str = Field(
        ..., example="acc_token_abc123", description="Tokenised account identifier"
    )
    merchant_id: str = Field(..., example="MER-001")
    merchant_category_code: str = Field(
        ..., example="5411", description="ISO 18245 MCC"
    )
    amount: Decimal = Field(
        ...,
        gt=0,
        example=1500.00,
        description="Transaction amount (BR-T1: Decimal precision)",
    )
    currency: str = Field(
        ...,
        min_length=3,
        max_length=3,
        example="ZAR",
        description="ISO 4217 currency code",
    )
    channel: str = Field(
        ...,
        example="CNP_ONLINE",
        description="One of: CNP_ONLINE, CNP_MOBILE, POS, ATM",
    )
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
    account_tier: str = Field(
        "STANDARD",
        example="STANDARD",
        description="One of: STANDARD, PREMIUM, BUSINESS",
    )


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
            transaction_id=getattr(txn, "transaction_id", ""),
            account_id_token=getattr(txn, "account_id_token", ""),
            merchant_id=getattr(txn, "merchant_id", ""),
            merchant_category_code=getattr(txn, "merchant_category_code", "5411"),
            amount=getattr(txn, "amount", Decimal("0.00")),
            currency=getattr(txn, "currency", "ZAR"),
            channel=getattr(
                getattr(txn, "channel", "CNP_ONLINE"),
                "value",
                getattr(txn, "channel", "CNP_ONLINE"),
            ),
            is_international=getattr(txn, "is_international", False),
            fraud_score=getattr(txn, "fraud_score", 0.0) or 0.0,
            risk_tier=getattr(
                getattr(txn, "risk_tier", "LOW"),
                "value",
                getattr(txn, "risk_tier", "LOW"),
            )
            or "LOW",
            decision=getattr(
                getattr(txn, "decision", None), "value", getattr(txn, "decision", None)
            ),
            model_version_composite=getattr(txn, "model_version_composite", "") or "",
            processing_ms=getattr(txn, "processing_ms", 0) or 0,
            pii_tokenised=getattr(txn, "pii_tokenised", True),
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
    risk_tier: str = Field(
        ..., example="CRITICAL", description="Must be HIGH or CRITICAL (FR-09)"
    )
    shap_report_ref: str = Field("", example="s3://shap-reports/TXN-2026-001.json")


class AssignAnalystRequest(BaseModel):
    """PATCH /api/fraud-cases/{id}/assign — assign case to a fraud analyst."""

    analyst_id: str = Field(..., example="j.mokoena", description="Analyst employee ID")


class ResolveCaseRequest(BaseModel):
    """PATCH /api/fraud-cases/{id}/resolve — resolve a case."""

    resolution: str = Field(
        ..., example="CONFIRMED", description="CONFIRMED or DISMISSED"
    )
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
            risk_tier=getattr(case.risk_tier, "value", case.risk_tier),
            priority=getattr(case.priority, "value", case.priority),
            status=getattr(case.status, "value", case.status),
            assigned_analyst_id=getattr(
                case,
                "assigned_analyst_id",
                getattr(case, "analyst_id", None),
            ),
            shap_report_ref=case.shap_report_ref,
            analyst_note=getattr(case, "analyst_note", getattr(case, "note", "")),
            created_at=getattr(
                case,
                "created_at",
                getattr(case, "opened_at", datetime.utcnow()),
            ),
            resolved_at=getattr(case, "resolved_at", None),
            sla_breach_at=getattr(
                case,
                "sla_breach_at",
                getattr(case, "created_at", getattr(case, "opened_at", datetime.utcnow())),
            ),
            is_breaching_sla=case.is_breaching_sla()
            if hasattr(case, "is_breaching_sla")
            else False,
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

    model_name: str = Field(
        ...,
        example="XGBOOST",
        description="One of: XGBOOST, ISOLATION_FOREST, DISTILBERT",
    )
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

    target_stage: str = Field(
        ...,
        example="STAGING",
        description="One of: STAGING, PRODUCTION, ARCHIVED, REJECTED",
    )


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
        precision = getattr(model, "precision", None)
        recall = getattr(model, "recall", None)

        if callable(getattr(model, "meets_promotion_gate", None)):
            try:
                meets_gate = model.meets_promotion_gate()
            except Exception:
                meets_gate = (precision or 0.0) >= 0.85 and (recall or 0.0) >= 0.80
        else:
            meets_gate = (precision or 0.0) >= 0.85 and (recall or 0.0) >= 0.80

        return cls(
            model_id=getattr(model, "model_id", getattr(model, "_model_id", "")),
            model_name=getattr(
                getattr(model, "model_name", getattr(model, "_model_name", "")),
                "value",
                getattr(model, "model_name", getattr(model, "_model_name", "")),
            ),
            version=getattr(model, "version", getattr(model, "_version", "")),
            stage=getattr(
                getattr(model, "stage", getattr(model, "_stage", "")),
                "value",
                getattr(model, "stage", getattr(model, "_stage", "")),
            ),
            precision=precision or 0.0,
            recall=recall or 0.0,
            f1_score=getattr(model, "f1_score", None) or 0.0,
            auc_roc=getattr(model, "auc_roc", None) or 0.0,
            artifact_path=getattr(
                model,
                "artifact_path",
                getattr(model, "artifact_uri", getattr(model, "_artifact_uri", "")),
            ),
            feature_schema_version=getattr(
                model,
                "feature_schema_version",
                getattr(model, "feature_set", getattr(model, "_feature_set", "")),
            ),
            meets_promotion_gate=meets_gate,
            trained_at=getattr(model, "trained_at", datetime.utcnow()),
            promoted_at=getattr(model, "promoted_at", None),
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
