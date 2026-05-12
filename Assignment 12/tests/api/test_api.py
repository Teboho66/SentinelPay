"""
Tests – REST API Integration Tests
=====================================
Uses FastAPI TestClient — full HTTP request/response cycle.
Each test class creates a fresh app instance with isolated in-memory repos.
"""

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient

import sys, os
for _p in ("../../Assignment10", "../../Assignment11"):
    _abs = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../" + _p.lstrip("../")))
    if _abs not in sys.path:
        sys.path.insert(0, _abs)

from api.main import app
from api import dependencies
from repositories.inmemory import (
    InMemoryTransactionRepository,
    InMemoryFraudCaseRepository,
    InMemoryMLModelRepository,
)
from services import TransactionService, FraudCaseService, MLModelService


# ── Isolated app fixture ──────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_repos():
    """Swap in fresh repos before every test to ensure full isolation."""
    txn_repo   = InMemoryTransactionRepository()
    case_repo  = InMemoryFraudCaseRepository()
    model_repo = InMemoryMLModelRepository()

    app.dependency_overrides[dependencies.get_transaction_service] = \
        lambda: TransactionService(txn_repo)
    app.dependency_overrides[dependencies.get_fraud_case_service] = \
        lambda: FraudCaseService(case_repo)
    app.dependency_overrides[dependencies.get_ml_model_service] = \
        lambda: MLModelService(model_repo)
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


# ── Shared payloads ───────────────────────────────────────────────────────────

TXN_PAYLOAD = {
    "transaction_id": "TXN-API-001",
    "account_id_token": "acc_token_abc",
    "merchant_id": "MER-001",
    "merchant_category_code": "5411",
    "amount": "1500.00",
    "currency": "ZAR",
    "channel": "CNP_ONLINE",
    "device_fingerprint_token": "dfp_abc",
    "ip_address_hash": "hash_abc",
    "latitude": -33.9249,
    "longitude": 18.4241,
    "is_international": False,
}

MODEL_SCORES = [
    {"model_name": "XGBOOST",          "model_version": "3.1", "raw_score": 0.95, "confidence": 0.98},
    {"model_name": "ISOLATION_FOREST", "model_version": "2.0", "raw_score": 0.88, "confidence": 0.85},
    {"model_name": "DISTILBERT",       "model_version": "1.4", "raw_score": 0.82, "confidence": 0.80},
]

MODEL_PAYLOAD = {
    "model_name": "XGBOOST",
    "version": "3.1",
    "artifact_path": "mlflow://models/xgboost/3.1",
    "feature_schema_version": "tabular-v3",
}


# ══════════════════════════════════════════════════════════════════════════════
# Transaction API Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestTransactionAPI:

    def test_health_check(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    def test_submit_transaction_returns_201(self, client):
        r = client.post("/api/transactions", json=TXN_PAYLOAD)
        assert r.status_code == 201

    def test_submit_returns_transaction_id(self, client):
        r = client.post("/api/transactions", json=TXN_PAYLOAD)
        assert r.json()["transaction_id"] == "TXN-API-001"

    def test_submit_pii_tokenised_in_response(self, client):
        r = client.post("/api/transactions", json=TXN_PAYLOAD)
        assert r.json()["pii_tokenised"] is True

    def test_submit_duplicate_returns_409(self, client):
        client.post("/api/transactions", json=TXN_PAYLOAD)
        r = client.post("/api/transactions", json=TXN_PAYLOAD)
        assert r.status_code == 409

    def test_submit_invalid_channel_returns_422(self, client):
        bad = {**TXN_PAYLOAD, "channel": "WIRE_TRANSFER"}
        r = client.post("/api/transactions", json=bad)
        assert r.status_code == 422

    def test_submit_negative_amount_returns_422(self, client):
        bad = {**TXN_PAYLOAD, "amount": "-100.00"}
        r = client.post("/api/transactions", json=bad)
        assert r.status_code == 422

    def test_get_all_transactions(self, client):
        client.post("/api/transactions", json=TXN_PAYLOAD)
        r = client.get("/api/transactions")
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_get_transaction_by_id(self, client):
        client.post("/api/transactions", json=TXN_PAYLOAD)
        r = client.get("/api/transactions/TXN-API-001")
        assert r.status_code == 200
        assert r.json()["transaction_id"] == "TXN-API-001"

    def test_get_nonexistent_transaction_returns_404(self, client):
        r = client.get("/api/transactions/MISSING")
        assert r.status_code == 404

    def test_apply_decision_returns_fraud_decision(self, client):
        client.post("/api/transactions", json=TXN_PAYLOAD)
        r = client.post("/api/transactions/TXN-API-001/decision", json={
            "fraud_score": 0.93,
            "model_scores": MODEL_SCORES,
            "account_tier": "STANDARD",
        })
        assert r.status_code == 200
        assert r.json()["decision"] == "HARD_BLOCK"

    def test_apply_decision_twice_returns_409(self, client):
        client.post("/api/transactions", json=TXN_PAYLOAD)
        payload = {"fraud_score": 0.93, "model_scores": MODEL_SCORES, "account_tier": "STANDARD"}
        client.post("/api/transactions/TXN-API-001/decision", json=payload)
        r = client.post("/api/transactions/TXN-API-001/decision", json=payload)
        assert r.status_code == 409

    def test_get_flagged_transactions(self, client):
        client.post("/api/transactions", json=TXN_PAYLOAD)
        client.post("/api/transactions/TXN-API-001/decision", json={
            "fraud_score": 0.93, "model_scores": MODEL_SCORES, "account_tier": "STANDARD"
        })
        r = client.get("/api/transactions/flagged")
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_filter_by_decision_query_param(self, client):
        client.post("/api/transactions", json=TXN_PAYLOAD)
        client.post("/api/transactions/TXN-API-001/decision", json={
            "fraud_score": 0.93, "model_scores": MODEL_SCORES, "account_tier": "STANDARD"
        })
        r = client.get("/api/transactions?decision=HARD_BLOCK")
        assert r.status_code == 200
        assert all(t["decision"] == "HARD_BLOCK" for t in r.json())

    def test_delete_transaction_returns_204(self, client):
        client.post("/api/transactions", json=TXN_PAYLOAD)
        r = client.delete("/api/transactions/TXN-API-001")
        assert r.status_code == 204

    def test_delete_nonexistent_returns_404(self, client):
        r = client.delete("/api/transactions/MISSING")
        assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# FraudCase API Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestFraudCaseAPI:

    CASE_PAYLOAD = {
        "transaction_id": "TXN-001",
        "account_id_token": "acc_token_001",
        "fraud_score": 0.93,
        "risk_tier": "CRITICAL",
        "shap_report_ref": "s3://shap/TXN-001.json",
    }

    def test_create_case_returns_201(self, client):
        r = client.post("/api/fraud-cases", json=self.CASE_PAYLOAD)
        assert r.status_code == 201

    def test_create_case_has_p1_priority(self, client):
        r = client.post("/api/fraud-cases", json=self.CASE_PAYLOAD)
        assert r.json()["priority"] == "P1"

    def test_create_case_status_is_open(self, client):
        r = client.post("/api/fraud-cases", json=self.CASE_PAYLOAD)
        assert r.json()["status"] == "OPEN"

    def test_create_case_low_tier_returns_422(self, client):
        bad = {**self.CASE_PAYLOAD, "risk_tier": "LOW", "fraud_score": 0.20}
        r = client.post("/api/fraud-cases", json=bad)
        assert r.status_code == 422

    def test_duplicate_case_returns_409(self, client):
        client.post("/api/fraud-cases", json=self.CASE_PAYLOAD)
        r = client.post("/api/fraud-cases", json=self.CASE_PAYLOAD)
        assert r.status_code == 409

    def test_get_all_cases(self, client):
        client.post("/api/fraud-cases", json=self.CASE_PAYLOAD)
        r = client.get("/api/fraud-cases")
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_get_case_by_id(self, client):
        r = client.post("/api/fraud-cases", json=self.CASE_PAYLOAD)
        case_id = r.json()["case_id"]
        r2 = client.get(f"/api/fraud-cases/{case_id}")
        assert r2.status_code == 200

    def test_get_analyst_queue_sorted_p1_first(self, client):
        client.post("/api/fraud-cases", json={**self.CASE_PAYLOAD, "transaction_id": "T1", "fraud_score": 0.65, "risk_tier": "HIGH"})
        client.post("/api/fraud-cases", json={**self.CASE_PAYLOAD, "transaction_id": "T2", "fraud_score": 0.95, "risk_tier": "CRITICAL"})
        r = client.get("/api/fraud-cases/queue")
        queue = r.json()
        assert queue[0]["priority"] == "P1"

    def test_assign_analyst(self, client):
        r = client.post("/api/fraud-cases", json=self.CASE_PAYLOAD)
        case_id = r.json()["case_id"]
        r2 = client.patch(f"/api/fraud-cases/{case_id}/assign",
                          json={"analyst_id": "j.mokoena"})
        assert r2.status_code == 200
        assert r2.json()["status"] == "IN_REVIEW"

    def test_resolve_confirmed(self, client):
        r = client.post("/api/fraud-cases", json=self.CASE_PAYLOAD)
        case_id = r.json()["case_id"]
        client.patch(f"/api/fraud-cases/{case_id}/assign", json={"analyst_id": "j.mokoena"})
        r2 = client.patch(f"/api/fraud-cases/{case_id}/resolve",
                          json={"resolution": "CONFIRMED", "note": "Confirmed fraud."})
        assert r2.status_code == 200
        assert r2.json()["case"]["status"] == "CONFIRMED"
        assert r2.json()["fraud_label_payload"] is not None

    def test_resolve_dismissed_without_note_returns_422(self, client):
        r = client.post("/api/fraud-cases", json=self.CASE_PAYLOAD)
        case_id = r.json()["case_id"]
        client.patch(f"/api/fraud-cases/{case_id}/assign", json={"analyst_id": "j.mokoena"})
        r2 = client.patch(f"/api/fraud-cases/{case_id}/resolve",
                          json={"resolution": "DISMISSED", "note": ""})
        assert r2.status_code == 422

    def test_delete_case_returns_204(self, client):
        r = client.post("/api/fraud-cases", json=self.CASE_PAYLOAD)
        case_id = r.json()["case_id"]
        client.patch(f"/api/fraud-cases/{case_id}/assign", json={"analyst_id": "j.mokoena"})
        client.patch(f"/api/fraud-cases/{case_id}/resolve",
                     json={"resolution": "DISMISSED", "note": "False positive confirmed."})
        r2 = client.delete(f"/api/fraud-cases/{case_id}")
        assert r2.status_code == 204


# ══════════════════════════════════════════════════════════════════════════════
# MLModel API Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestMLModelAPI:

    def test_register_model_returns_201(self, client):
        r = client.post("/api/ml-models", json=MODEL_PAYLOAD)
        assert r.status_code == 201

    def test_register_model_stage_is_training(self, client):
        r = client.post("/api/ml-models", json=MODEL_PAYLOAD)
        assert r.json()["stage"] == "TRAINING"

    def test_register_duplicate_returns_409(self, client):
        client.post("/api/ml-models", json=MODEL_PAYLOAD)
        r = client.post("/api/ml-models", json=MODEL_PAYLOAD)
        assert r.status_code == 409

    def test_register_invalid_model_name_returns_422(self, client):
        bad = {**MODEL_PAYLOAD, "model_name": "NEURAL_NET"}
        r = client.post("/api/ml-models", json=bad)
        assert r.status_code == 422

    def test_get_all_models(self, client):
        client.post("/api/ml-models", json=MODEL_PAYLOAD)
        r = client.get("/api/ml-models")
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_evaluate_model(self, client):
        r = client.post("/api/ml-models", json=MODEL_PAYLOAD)
        model_id = r.json()["model_id"]
        r2 = client.post(f"/api/ml-models/{model_id}/evaluate",
                         json={"precision": 0.91, "recall": 0.87,
                               "f1_score": 0.89, "auc_roc": 0.94})
        assert r2.status_code == 200
        assert r2.json()["meets_promotion_gate"] is True

    def test_evaluate_failing_gate(self, client):
        r = client.post("/api/ml-models", json=MODEL_PAYLOAD)
        model_id = r.json()["model_id"]
        r2 = client.post(f"/api/ml-models/{model_id}/evaluate",
                         json={"precision": 0.80, "recall": 0.70,
                               "f1_score": 0.74, "auc_roc": 0.81})
        assert r2.json()["meets_promotion_gate"] is False

    def test_promote_to_staging(self, client):
        r = client.post("/api/ml-models", json=MODEL_PAYLOAD)
        model_id = r.json()["model_id"]
        r2 = client.patch(f"/api/ml-models/{model_id}/promote",
                          json={"target_stage": "STAGING"})
        assert r2.status_code == 200
        assert r2.json()["stage"] == "STAGING"

    def test_promote_to_production_passes_gate(self, client):
        r = client.post("/api/ml-models", json=MODEL_PAYLOAD)
        model_id = r.json()["model_id"]
        client.post(f"/api/ml-models/{model_id}/evaluate",
                    json={"precision": 0.91, "recall": 0.87, "f1_score": 0.89, "auc_roc": 0.94})
        client.patch(f"/api/ml-models/{model_id}/promote", json={"target_stage": "STAGING"})
        r2 = client.patch(f"/api/ml-models/{model_id}/promote", json={"target_stage": "PRODUCTION"})
        assert r2.status_code == 200
        assert r2.json()["stage"] == "PRODUCTION"

    def test_promote_to_production_fails_gate(self, client):
        r = client.post("/api/ml-models", json=MODEL_PAYLOAD)
        model_id = r.json()["model_id"]
        client.post(f"/api/ml-models/{model_id}/evaluate",
                    json={"precision": 0.80, "recall": 0.70, "f1_score": 0.74, "auc_roc": 0.81})
        client.patch(f"/api/ml-models/{model_id}/promote", json={"target_stage": "STAGING"})
        r2 = client.patch(f"/api/ml-models/{model_id}/promote", json={"target_stage": "PRODUCTION"})
        assert r2.status_code == 422

    def test_hot_swap_production_model(self, client):
        r = client.post("/api/ml-models", json=MODEL_PAYLOAD)
        model_id = r.json()["model_id"]
        client.post(f"/api/ml-models/{model_id}/evaluate",
                    json={"precision": 0.91, "recall": 0.87, "f1_score": 0.89, "auc_roc": 0.94})
        client.patch(f"/api/ml-models/{model_id}/promote", json={"target_stage": "STAGING"})
        client.patch(f"/api/ml-models/{model_id}/promote", json={"target_stage": "PRODUCTION"})
        r2 = client.patch(f"/api/ml-models/{model_id}/hot-swap",
                          json={"new_artifact_path": "mlflow://xgb/3.1-hotfix"})
        assert r2.status_code == 200
        assert r2.json()["artifact_path"] == "mlflow://xgb/3.1-hotfix"

    def test_hot_swap_non_production_returns_409(self, client):
        r = client.post("/api/ml-models", json=MODEL_PAYLOAD)
        model_id = r.json()["model_id"]
        r2 = client.patch(f"/api/ml-models/{model_id}/hot-swap",
                          json={"new_artifact_path": "mlflow://xgb/3.1-hotfix"})
        assert r2.status_code == 409

    def test_get_production_models(self, client):
        r = client.post("/api/ml-models", json=MODEL_PAYLOAD)
        model_id = r.json()["model_id"]
        client.post(f"/api/ml-models/{model_id}/evaluate",
                    json={"precision": 0.91, "recall": 0.87, "f1_score": 0.89, "auc_roc": 0.94})
        client.patch(f"/api/ml-models/{model_id}/promote", json={"target_stage": "STAGING"})
        client.patch(f"/api/ml-models/{model_id}/promote", json={"target_stage": "PRODUCTION"})
        r2 = client.get("/api/ml-models/production")
        assert r2.status_code == 200
        assert len(r2.json()) == 1

    def test_delete_training_model_returns_204(self, client):
        r = client.post("/api/ml-models", json=MODEL_PAYLOAD)
        model_id = r.json()["model_id"]
        r2 = client.delete(f"/api/ml-models/{model_id}")
        assert r2.status_code == 204

    def test_delete_production_returns_422(self, client):
        r = client.post("/api/ml-models", json=MODEL_PAYLOAD)
        model_id = r.json()["model_id"]
        client.post(f"/api/ml-models/{model_id}/evaluate",
                    json={"precision": 0.91, "recall": 0.87, "f1_score": 0.89, "auc_roc": 0.94})
        client.patch(f"/api/ml-models/{model_id}/promote", json={"target_stage": "STAGING"})
        client.patch(f"/api/ml-models/{model_id}/promote", json={"target_stage": "PRODUCTION"})
        r2 = client.delete(f"/api/ml-models/{model_id}")
        assert r2.status_code == 422