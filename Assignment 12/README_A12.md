# Assignment 12 – SentinelPay: Service Layer and REST API

## Overview

Assignment 12 implements the **service layer** and **REST API layer** for SentinelPay on top of:

* Assignment 10 domain models
* Assignment 11 repository interfaces and in-memory repositories

The implementation covers three main entities end-to-end:

* **Transaction**
* **FraudCase**
* **MLModel**

Together, these entities represent the fraud detection workflow from transaction submission, to fraud decisioning, to analyst case handling, and finally to ML model lifecycle management.

All Assignment 12 tests pass:

```bash
116 passed
```

---

## Directory Structure

```text
Assignment 12/
├── api/
│   ├── __init__.py
│   ├── dependencies.py          # Compatibility re-export for dependency wiring
│   └── main.py                  # FastAPI app, router registration, OpenAPI config
│
├── config/
│   ├── dependencies.py          # Repository and service dependency injection
│   └── schemas.py               # Pydantic request/response models
│
├── handlers/
│   └── routes/
│       ├── transactions.py      # Transaction REST endpoints
│       ├── fraud_cases.py       # FraudCase REST endpoints
│       └── ml_models.py         # MLModel REST endpoints
│
├── mapping/
│   ├── transaction_service.py   # TransactionService business logic
│   ├── fraud_case_service.py    # FraudCaseService business logic
│   └── ml_model_service.py      # MLModelService business logic
│
├── repositories/
│   ├── interfaces.py
│   ├── base.py
│   ├── implementations.py
│   └── inmemory/
│       ├── base_inmemory.py
│       └── implementations.py
│
├── services/
│   ├── __init__.py
│   └── exceptions.py            # Domain/service exceptions
│
├── tests/
│   ├── api/
│   │   └── test_api.py
│   └── services/
│       ├── test_transaction_service.py
│       ├── test_fraud_case_service.py
│       └── test_ml_model_service.py
│
├── docs/
│   └── openapi.json
│
├── conftest.py
├── pytest.ini
├── README_A12.md
└── CHANGELOG_A12.md
```

---

## 1. Service Layer

### Architecture

The service layer sits between the FastAPI route handlers and the repository layer.

```text
HTTP Request
    ↓
Pydantic Request Schema
    ↓
Route Handler
    ↓
Service Layer
    ↓
Repository Interface
    ↓
In-Memory Repository
```

Services are responsible for:

* Accepting plain Python values as input
* Enforcing business rules
* Calling repository interfaces
* Raising domain-specific exceptions
* Returning domain objects to the API layer

The API layer converts these domain objects into Pydantic response models.

---

## 2. Implemented Services

### TransactionService

Located at:

```text
mapping/transaction_service.py
```

Main responsibilities:

| Method                       | Description                                  |
| ---------------------------- | -------------------------------------------- |
| `submit_transaction()`       | Creates and stores a transaction             |
| `apply_fraud_decision()`     | Applies fraud score, decision, and risk tier |
| `get_transaction()`          | Retrieves a transaction by ID                |
| `get_all_transactions()`     | Returns all transactions                     |
| `get_flagged_transactions()` | Returns HARD_BLOCK transactions              |
| `get_by_decision()`          | Filters transactions by fraud decision       |
| `get_by_risk_tier()`         | Filters transactions by risk tier            |
| `delete_transaction()`       | Deletes a transaction                        |

Business rules covered:

* Duplicate transaction IDs are rejected
* Invalid transaction channels are rejected
* Account IDs are tokenised with the `acc_token_` prefix
* Fraud decisions are applied only once
* High fraud scores result in `HARD_BLOCK`
* Medium fraud scores result in `SOFT_DECLINE`
* Low fraud scores result in `APPROVE`

---

### FraudCaseService

Located at:

```text
mapping/fraud_case_service.py
```

Main responsibilities:

| Method                | Description                                     |
| --------------------- | ----------------------------------------------- |
| `create_case()`       | Creates a fraud investigation case              |
| `assign_to_analyst()` | Assigns an OPEN case to an analyst              |
| `resolve_case()`      | Resolves a case as CONFIRMED or DISMISSED       |
| `get_analyst_queue()` | Returns open/in-review cases sorted by priority |
| `get_by_priority()`   | Filters cases by priority                       |
| `get_by_status()`     | Filters cases by status                         |
| `delete_case()`       | Deletes eligible cases                          |

Business rules covered:

* Fraud cases are only created for `HIGH` or `CRITICAL` risk tiers
* One case is allowed per transaction
* Case priority is derived from fraud score:

  * `P1` for scores `>= 0.90`
  * `P2` for scores `>= 0.75`
  * `P3` for scores `< 0.75`
* Assigning a case moves it from `OPEN` to `IN_REVIEW`
* Resolving a `DISMISSED` case requires an analyst note
* Resolving a `CONFIRMED` case returns a fraud label payload
* Confirmed cases cannot be deleted

---

### MLModelService

Located at:

```text
mapping/ml_model_service.py
```

Main responsibilities:

| Method                    | Description                              |
| ------------------------- | ---------------------------------------- |
| `register_model()`        | Registers a new ML model version         |
| `evaluate_model()`        | Records model evaluation metrics         |
| `promote_model()`         | Promotes models through lifecycle stages |
| `hot_swap_artifact()`     | Replaces production model artifact path  |
| `get_production_models()` | Returns production models                |
| `get_by_stage()`          | Filters models by lifecycle stage        |
| `get_by_model_name()`     | Filters models by model name             |
| `delete_model()`          | Deletes non-production models            |

Business rules covered:

* Valid model names are enforced
* Duplicate model IDs are rejected
* Models start in `TRAINING`
* Evaluation returns:

  * the updated model
  * evaluation metrics
  * promotion gate result
* Promotion to `PRODUCTION` requires:

  * precision `>= 0.85`
  * recall `>= 0.80`
* Only one production model per model name is allowed
* Previous production model is archived when a new one is promoted
* Production models cannot be deleted
* Hot-swap is only allowed for production models

---

## 3. Exception Mapping

Exceptions are defined in:

```text
services/exceptions.py
```

The API layer maps service exceptions to HTTP responses.

| Exception                     | HTTP Status | Meaning                                         |
| ----------------------------- | ----------: | ----------------------------------------------- |
| `EntityNotFoundError`         |         404 | Entity does not exist                           |
| `DuplicateEntityError`        |         409 | Duplicate entity or unique constraint violation |
| `InvalidStateTransitionError` |         409 | Operation is invalid for the current state      |
| `BusinessRuleViolationError`  |         422 | Business rule validation failed                 |
| `PromotionGateFailedError`    |         422 | ML promotion gate failed                        |

---

## 4. REST API

The FastAPI application is defined in:

```text
api/main.py
```

Routes are defined in:

```text
handlers/routes/
```

Schemas are defined in:

```text
config/schemas.py
```

Dependency injection is defined in:

```text
config/dependencies.py
```

---

## 5. Running the API

From the repository root:

```bash
cd "Assignment 12"
PYTHONPATH=".:../Assignment 10:../Assignment 11" uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

```text
http://localhost:8000/docs
```

In GitHub Codespaces, open the forwarded port 8000 URL and add:

```text
/docs
```

Example:

```text
https://<your-codespace>-8000.app.github.dev/docs
```

Useful API URLs:

```text
/               Root API message
/health         Health check
/docs           Swagger UI
/redoc          ReDoc documentation
/openapi.json   OpenAPI schema
```

---

## 6. API Endpoints

### Transactions

Base path:

```text
/api/transactions
```

| Method   | Endpoint                                      | Description                 |
| -------- | --------------------------------------------- | --------------------------- |
| `POST`   | `/api/transactions`                           | Submit a transaction        |
| `GET`    | `/api/transactions`                           | Get all transactions        |
| `GET`    | `/api/transactions/flagged`                   | Get HARD_BLOCK transactions |
| `GET`    | `/api/transactions/{transaction_id}`          | Get transaction by ID       |
| `POST`   | `/api/transactions/{transaction_id}/decision` | Apply fraud decision        |
| `DELETE` | `/api/transactions/{transaction_id}`          | Delete transaction          |

---

### Fraud Cases

Base path:

```text
/api/fraud-cases
```

| Method   | Endpoint                             | Description         |
| -------- | ------------------------------------ | ------------------- |
| `POST`   | `/api/fraud-cases`                   | Create fraud case   |
| `GET`    | `/api/fraud-cases`                   | Get all fraud cases |
| `GET`    | `/api/fraud-cases/queue`             | Get analyst queue   |
| `GET`    | `/api/fraud-cases/{case_id}`         | Get case by ID      |
| `PATCH`  | `/api/fraud-cases/{case_id}/assign`  | Assign analyst      |
| `PATCH`  | `/api/fraud-cases/{case_id}/resolve` | Resolve case        |
| `DELETE` | `/api/fraud-cases/{case_id}`         | Delete case         |

---

### ML Models

Base path:

```text
/api/ml-models
```

| Method   | Endpoint                             | Description             |
| -------- | ------------------------------------ | ----------------------- |
| `POST`   | `/api/ml-models`                     | Register model          |
| `GET`    | `/api/ml-models`                     | Get all models          |
| `GET`    | `/api/ml-models/production`          | Get production models   |
| `GET`    | `/api/ml-models/{model_id}`          | Get model by ID         |
| `POST`   | `/api/ml-models/{model_id}/evaluate` | Evaluate model          |
| `PATCH`  | `/api/ml-models/{model_id}/promote`  | Promote model           |
| `PATCH`  | `/api/ml-models/{model_id}/hot-swap` | Hot-swap model artifact |
| `DELETE` | `/api/ml-models/{model_id}`          | Delete model            |

---

## 7. Running Tests

From the repository root:

```bash
PYTHONPATH="Assignment 12:Assignment 10:Assignment 11" pytest "Assignment 12/tests"
```

Expected result:

```text
116 passed
```

To run all assignment test suites separately:

```bash
PYTHONPATH="Assignment 10/FraudRule:Assignment 10:Assignment 10/src" pytest "Assignment 10/tests"

PYTHONPATH="Assignment 11:Assignment 10" pytest "Assignment 11/tests"

PYTHONPATH="Assignment 12:Assignment 10:Assignment 11" pytest "Assignment 12/tests"
```

---

## 8. Linting

Run Ruff from the repository root:

```bash
ruff check .
```

Expected result:

```text
All checks passed!
```

---

## 9. Notes About Warnings

The test suite currently shows deprecation warnings from FastAPI and Pydantic, mainly related to:

* `example=...` in Pydantic `Field`
* `example=...` in FastAPI `Query`
* `datetime.utcnow()`

These warnings do not affect functionality and do not cause tests to fail.

---

## 10. Completion Summary

Assignment 12 delivers:

* Service layer for Transaction, FraudCase, and MLModel
* REST API endpoints for all three entities
* Dependency injection using in-memory repositories
* Pydantic request and response schemas
* OpenAPI/Swagger documentation
* Business-rule exception handling
* Full API and service test coverage

Final test result:

```text
116 passed
```
