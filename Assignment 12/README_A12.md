# Assignment 12 – SentinelPay: Service Layer and REST API

## Overview

This assignment builds the service and API layers on top of the domain model (A10)
and repository layer (A11). Three entities are fully implemented end-to-end:
**Transaction**, **FraudCase**, and **MLModel** — chosen because they cover the
complete fraud detection pipeline from transaction ingestion through analyst
case resolution and ML model lifecycle management.

---

## Directory Structure

```
Assignment 12/
├── services/
│   ├── exceptions.py            ← Domain exceptions → HTTP status code mapping
│   ├── transaction_service.py   ← TransactionService (FR-01–FR-08)
│   ├── fraud_case_service.py    ← FraudCaseService (FR-09–FR-10)
│   └── ml_model_service.py      ← MLModelService (FR-13–FR-14)
│
├── api/
│   ├── main.py                  ← FastAPI app, router registration, OpenAPI config
│   ├── schemas.py               ← Pydantic request/response models (18 schemas)
│   ├── dependencies.py          ← DI wiring: repos → services → route handlers
│   └── routes/
│       ├── transactions.py      ← 6 Transaction endpoints
│       ├── fraud_cases.py       ← 7 FraudCase endpoints
│       └── ml_models.py         ← 8 MLModel endpoints
│
├── tests/
│   ├── services/
│   │   ├── test_transaction_service.py   ← 20 service unit tests
│   │   ├── test_fraud_case_service.py    ← 27 service unit tests
│   │   └── test_ml_model_service.py      ← 32 service unit tests
│   └── api/
│       └── test_api.py                  ← 37 API integration tests
│
├── docs/
│   └── openapi.json             ← Full OpenAPI 3.1 specification (auto-generated)
│
├── conftest.py
├── pytest.ini
├── README_A12.md
└── CHANGELOG_A12.md
```

---

## 1. Service Layer

### Architecture

The service layer sits between the API (HTTP concerns) and repositories (storage
concerns). Services:
- Accept plain Python types as input (not HTTP schemas, not domain entities)
- Enforce all SentinelPay business rules from the SRD
- Raise domain exceptions that the API layer maps to HTTP status codes
- Are injected with a repository interface — storage backend is irrelevant

```
HTTP Request → Pydantic Schema → Route Handler → Service → Repository → Storage
                                      ↓
                               HTTP Response ← Pydantic Schema ← Domain Entity
```

### TransactionService

| Method | Business rule enforced | HTTP status |
|---|---|---|
| `submit_transaction()` | FR-02 validate(), BR-T2 tokenise_pii() | 201 / 409 / 422 |
| `apply_fraud_decision()` | FR-07 ensemble weighting + per-tier thresholds | 200 / 409 / 422 |
| `get_flagged_transactions()` | FR-09 HARD_BLOCK filter for case pipeline | 200 |

### FraudCaseService

| Method | Business rule enforced | HTTP status |
|---|---|---|
| `create_case()` | FR-09: HIGH/CRITICAL only; one case per transaction | 201 / 409 / 422 |
| `assign_to_analyst()` | FR-10: case must be OPEN; analyst_id required | 200 / 409 / 422 |
| `resolve_case()` | BR-FC2: DISMISSED needs note; BR-FC3: CONFIRMED emits label | 200 / 409 / 422 |
| `get_analyst_queue()` | FR-10: sorted P1 → P2 → P3, SLA breach flagged | 200 |

### MLModelService

| Method | Business rule enforced | HTTP status |
|---|---|---|
| `register_model()` | FR-13: valid ModelName, unique model_id | 201 / 409 / 422 |
| `evaluate_model()` | BR-ML1: precision ≥ 0.85 AND recall ≥ 0.80 gate | 200 / 404 |
| `promote_model()` | FR-13: lifecycle graph; BR-ML1 on PRODUCTION; auto-archive old PRODUCTION | 200 / 409 / 422 |
| `hot_swap_artifact()` | FR-14: PRODUCTION-only; blank path rejected | 200 / 409 |

### Exception → HTTP Status Mapping

| Exception | HTTP Status | When raised |
|---|---|---|
| `EntityNotFoundError` | 404 | Entity not found by ID |
| `DuplicateEntityError` | 409 | Unique constraint violated |
| `InvalidStateTransitionError` | 409 | Operation invalid for current state |
| `BusinessRuleViolationError` | 422 | SRD business rule violated |
| `PromotionGateFailedError` | 422 | BR-ML1 precision/recall not met |

---

## 2. REST API

### Running the API

```bash
# From Assignment 12 root
pip install fastapi uvicorn httpx
uvicorn api.main:app --reload --port 8000
```

Then visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json
- **Health check:** http://localhost:8000/health

### Endpoint Summary

#### Transactions (`/api/transactions`)

| Method | Endpoint | Description | Status codes |
|---|---|---|---|
| `POST` | `/api/transactions` | Submit transaction for fraud evaluation | 201, 409, 422 |
| `GET` | `/api/transactions` | Fetch all transactions (filter by decision/risk_tier) | 200, 422 |
| `GET` | `/api/transactions/flagged` | All HARD_BLOCK transactions (FR-09 pipeline) | 200 |
| `GET` | `/api/transactions/{id}` | Get transaction by ID | 200, 404 |
| `POST` | `/api/transactions/{id}/decision` | Apply ML ensemble fraud decision | 200, 404, 409, 422 |
| `DELETE` | `/api/transactions/{id}` | Delete a transaction | 204, 404 |

#### Fraud Cases (`/api/fraud-cases`)

| Method | Endpoint | Description | Status codes |
|---|---|---|---|
| `POST` | `/api/fraud-cases` | Create fraud investigation case | 201, 409, 422 |
| `GET` | `/api/fraud-cases` | Get all cases (filter by status/priority) | 200, 422 |
| `GET` | `/api/fraud-cases/queue` | Analyst queue sorted P1→P2→P3 | 200 |
| `GET` | `/api/fraud-cases/{id}` | Get case by ID | 200, 404 |
| `PATCH` | `/api/fraud-cases/{id}/assign` | Assign case to analyst | 200, 404, 409 |
| `PATCH` | `/api/fraud-cases/{id}/resolve` | Resolve as CONFIRMED or DISMISSED | 200, 404, 409, 422 |
| `DELETE` | `/api/fraud-cases/{id}` | Delete dismissed case | 204, 404, 422 |

#### ML Models (`/api/ml-models`)

| Method | Endpoint | Description | Status codes |
|---|---|---|---|
| `POST` | `/api/ml-models` | Register new model version | 201, 409, 422 |
| `GET` | `/api/ml-models` | All models (filter by stage/model_name) | 200, 422 |
| `GET` | `/api/ml-models/production` | All PRODUCTION models (FR-14 hot-swap poll) | 200 |
| `GET` | `/api/ml-models/{id}` | Get model by ID | 200, 404 |
| `POST` | `/api/ml-models/{id}/evaluate` | Record evaluation metrics | 200, 404, 409 |
| `PATCH` | `/api/ml-models/{id}/promote` | Promote through lifecycle stages | 200, 404, 409, 422 |
| `PATCH` | `/api/ml-models/{id}/hot-swap` | Reload artifact in PRODUCTION | 200, 404, 409 |
| `DELETE` | `/api/ml-models/{id}` | Delete non-PRODUCTION model | 204, 404, 422 |

---

## 3. API Documentation

FastAPI auto-generates the full OpenAPI 3.1 specification from code annotations.
The exported spec is available at `docs/openapi.json` (16 paths, 18 schemas).

Every endpoint includes:
- Human-readable `summary` and `description` with FR/business rule references
- Documented `request body` with field-level validation (`gt`, `ge`, `le`, `min_length`)
- Complete `responses` dict with per-status-code descriptions and error schemas
- `tags` grouping endpoints by domain (`Transactions`, `Fraud Cases`, `ML Models`)

**Example — apply decision endpoint documentation:**
```python
@router.post(
    "/{transaction_id}/decision",
    response_model=TransactionResponse,
    summary="Apply fraud decision to a transaction",
    description="FR-07: Applies ML ensemble scores, computes composite fraud_score...",
    responses={
        200: {"description": "Decision applied"},
        404: {"model": ErrorResponse, "description": "Transaction not found"},
        409: {"model": ErrorResponse, "description": "Decision already applied"},
        422: {"model": ErrorResponse, "description": "Invalid model scores"},
    },
)
```

---

## 4. Dependency Injection

`api/dependencies.py` wires repositories into services using FastAPI's `Depends`
system. Switching to a real database backend requires changing only this file —
all route handlers are untouched:

```python
# Current: in-memory (tests / local dev)
_transaction_repo = InMemoryTransactionRepository()

# Future: swap to database
_transaction_repo = DatabaseTransactionRepository(connection_string=DATABASE_URL)

def get_transaction_service() -> TransactionService:
    return TransactionService(_transaction_repo)
```

Integration tests override dependencies per test using `app.dependency_overrides`,
ensuring each test runs with a completely fresh in-memory store.

---

## Running the Tests

```bash
pip install fastapi uvicorn httpx pytest pytest-cov
pytest tests/ -v
pytest tests/ --cov=services --cov=api --cov-report=term-missing
```

### Test Coverage

| Module | Tests | Coverage |
|---|---|---|
| `services/transaction_service.py` | 20 | 95% |
| `services/fraud_case_service.py` | 27 | 97% |
| `services/ml_model_service.py` | 32 | 96% |
| `api/routes/transactions.py` | (integration) | 91% |
| `api/routes/fraud_cases.py` | (integration) | 93% |
| `api/routes/ml_models.py` | (integration) | 92% |
| **Total — 116 tests** | | **~94%** |

---

## GitHub Issues

- `Close #23: Implement TransactionService with FR-01–FR-08 business rules`
- `Close #24: Implement FraudCaseService with FR-09–FR-10 + BR-FC2 + BR-FC3`
- `Close #25: Implement MLModelService with FR-13–FR-14 + BR-ML1 promotion gate`
- `Close #26: Build Transaction REST API (6 endpoints)`
- `Close #27: Build FraudCase REST API (7 endpoints)`
- `Close #28: Build MLModel REST API (8 endpoints)`
- `Close #29: Export OpenAPI 3.1 spec (16 paths, 18 schemas)`
- `Close #30: API integration tests with dependency injection overrides`