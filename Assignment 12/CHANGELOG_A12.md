# CHANGELOG – Assignment 12

### Added

**Service Layer (`/services`)**
- `exceptions.py` — 5 domain exceptions: `EntityNotFoundError` (404), `DuplicateEntityError` (409), `InvalidStateTransitionError` (409), `BusinessRuleViolationError` (422), `PromotionGateFailedError` (422)
- `transaction_service.py` — `TransactionService`: `submit_transaction()` enforcing FR-02 + BR-T2; `apply_fraud_decision()` with 60/25/15 ensemble weighting and per-tier thresholds (STANDARD/PREMIUM/BUSINESS); full query suite (`get_flagged_transactions()`, `get_by_decision()`, `get_by_risk_tier()`)
- `fraud_case_service.py` — `FraudCaseService`: `create_case()` enforcing FR-09 HIGH/CRITICAL-only rule + uniqueness; `assign_to_analyst()` with state guard; `resolve_case()` enforcing BR-FC2 (DISMISSED needs note) and BR-FC3 (CONFIRMED emits label payload); `get_analyst_queue()` sorted P1 → P2 → P3
- `ml_model_service.py` — `MLModelService`: `register_model()` with auto-generated model_id; `evaluate_model()` recording EvaluationMetrics; `promote_model()` enforcing lifecycle graph + BR-ML1 gate + auto-archiving old PRODUCTION; `hot_swap_artifact()` (FR-14)

**REST API (`/api`)**
- `schemas.py` — 18 Pydantic schemas: `SubmitTransactionRequest`, `ApplyDecisionRequest`, `TransactionResponse`, `CreateFraudCaseRequest`, `AssignAnalystRequest`, `ResolveCaseRequest`, `FraudCaseResponse`, `ResolveCaseResponse`, `RegisterModelRequest`, `EvaluateModelRequest`, `PromoteModelRequest`, `HotSwapRequest`, `MLModelResponse`, `EvaluateModelResponse`, `ErrorResponse` + helpers
- `dependencies.py` — FastAPI dependency injection wiring repositories → services; `app.dependency_overrides` support for test isolation
- `routes/transactions.py` — 6 endpoints: POST (submit), GET (all + filter), GET /flagged, GET /{id}, POST /{id}/decision, DELETE /{id}
- `routes/fraud_cases.py` — 7 endpoints: POST (create), GET (all + filter), GET /queue (sorted), GET /{id}, PATCH /{id}/assign, PATCH /{id}/resolve, DELETE /{id}
- `routes/ml_models.py` — 8 endpoints: POST (register), GET (all + filter), GET /production, GET /{id}, POST /{id}/evaluate, PATCH /{id}/promote, PATCH /{id}/hot-swap, DELETE /{id}
- `main.py` — FastAPI app with full OpenAPI metadata, tag descriptions, contact info, 3 routers, `/health` endpoint

**Tests (`/tests`)**
- `tests/services/test_transaction_service.py` — 20 unit tests: submit + PII tokenisation, duplicate guard, invalid channel/currency, decision outcomes (HARD_BLOCK/APPROVE/SOFT_DECLINE), idempotent state guard, query filters, delete
- `tests/services/test_fraud_case_service.py` — 27 unit tests: LOW/MEDIUM tier rejection, P1/P2/P3 priority, duplicate guard, analyst assignment state guards, BR-FC2 note enforcement, BR-FC3 label payload, queue sorting, delete guards
- `tests/services/test_ml_model_service.py` — 32 unit tests: model_id auto-generation, duplicate guard, gate pass/fail (precision-only fail, recall-only fail), lifecycle graph enforcement, auto-archive of old PRODUCTION, hot-swap, all query methods
- `tests/api/test_api.py` — 37 integration tests using `TestClient` + `dependency_overrides` for full isolation; covers all endpoints + status codes + error responses

**Documentation (`/docs`)**
- `openapi.json` — Full OpenAPI 3.1 spec auto-exported from FastAPI (16 paths, 18 schemas); accessible at `/openapi.json` when server running

### GitHub Issues to Close

- `Close #23` — TransactionService
- `Close #24` — FraudCaseService  
- `Close #25` — MLModelService
- `Close #26` — Transaction REST API
- `Close #27` — FraudCase REST API
- `Close #28` — MLModel REST API
- `Close #29` — OpenAPI spec export
- `Close #30` — API integration tests

### Push command

```bash
git add "Assignment 12/"
git commit -m "Close #23 #24 #25 #26 #27 #28 #29 #30: Assignment 12 service layer and REST API — 116 tests passing"
git push origin main
```