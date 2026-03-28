# TEST_CASES.md - Test Case Development
## SentinelPay: Real-Time Fraud Detection & Prevention Engine

> **Assignment 5 - Test Case Development**
> All test cases trace directly to functional requirements (FR) and non-functional requirements (NFR) defined in SRD.md
> Test cases validate the use cases specified in USE_CASE_SPECIFICATIONS.md

---

## 1. Test Case Overview

| Category | Count |
|---|---|
| Functional Test Cases | 10 |
| Non-Functional Test Scenarios | 2 |
| **Total** | **12** |

**Test environment:** Docker Compose local stack running all SentinelPay services. Kafka, PostgreSQL, Redis, and Cassandra all running. ML models loaded from MLflow.

---

## 2. Functional Test Cases

| Test Case ID | Requirement ID | Use Case | Description | Pre-conditions | Test Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|---|---|
| **TC-001** | FR-01 | UC1 | Valid transaction ingested and enriched within latency SLA | Kafka broker running. Ingestion Service consuming from `transactions.raw`. Redis available. | 1. Publish a valid JSON transaction payload to `transactions.raw`. 2. Record the publication timestamp. 3. Poll `transactions.enriched` for the enriched event. 4. Record the consumption timestamp. | Enriched event appears on `transactions.enriched` within 5ms of publication (P99). Event contains tokenised PII fields and a schema version header. | - | - |
| **TC-002** | FR-02 | UC1 | Transaction with missing mandatory field is dead-lettered | Ingestion Service running. `transactions.dlq` topic exists. | 1. Publish a transaction payload with `amount` field removed. 2. Poll `transactions.dlq` for the rejected event. 3. Inspect the error payload. | Event appears on `transactions.dlq` within 2ms. Error payload contains `error_code: SCHEMA_VALIDATION_FAILED` and lists `amount` as the missing field. Event does NOT appear on `transactions.enriched`. | - | - |
| **TC-003** | FR-03 | UC1 | PII fields are tokenised before downstream publication | Ingestion Service running. Token vault service available. | 1. Publish a transaction with known `account_id: ACC-12345`. 2. Consume the enriched event from `transactions.enriched`. 3. Inspect all fields in the enriched payload. | The enriched payload contains `account_id_token: acc_token_xxxx` (a token reference). The raw value `ACC-12345` does not appear anywhere in the enriched payload. | - | - |
| **TC-004** | FR-04 | UC3 | ML ensemble produces a fraud score and risk tier for every valid transaction | ML Scoring Service running. All 3 models loaded. Feature Engineering Service available. | 1. Publish a valid transaction to `transactions.raw`. 2. Allow pipeline to process through to `transactions.scored`. 3. Consume the scored result from `transactions.scored`. | Scored result contains: `fraud_score` (float between 0.0 and 1.0), `risk_tier` (one of LOW/MEDIUM/HIGH/CRITICAL), `model_version_composite` (non-empty string), `processing_ms` (integer > 0). | - | - |
| **TC-005** | FR-06 | UC4 | Transaction matching a blacklisted merchant is HARD_BLOCKED without ML scoring | Decision Engine running. Pre-filter rules configured with merchant blacklist entry for `merchant_id: MCH-BLACKLIST-001`. | 1. Publish a transaction with `merchant_id: MCH-BLACKLIST-001`. 2. Consume the decision from `transactions.decisions`. 3. Inspect the decision payload. | Decision is `HARD_BLOCK`. Field `rule_triggers` contains `MERCHANT_BLACKLIST_MATCH`. The scored result on `transactions.scored` shows `pre_filter_block: true`. ML ensemble was not invoked. | - | - |
| **TC-006** | FR-07 | UC4 | High fraud score transaction receives HARD_BLOCK decision | Decision Engine running. Standard tier thresholds configured (HARD_BLOCK at fraud_score >= 0.80). | 1. Inject a pre-scored transaction with `fraud_score: 0.92` and `risk_tier: CRITICAL` directly to `transactions.scored`. 2. Consume the decision from `transactions.decisions`. | Decision is `HARD_BLOCK`. `threshold_applied` reflects the Standard tier HARD_BLOCK threshold (0.80). Decision record persisted in PostgreSQL with all required fields including `decided_at` timestamp. | - | - |
| **TC-007** | FR-08 | UC5 | SOFT_DECLINE triggers step-up OTP challenge delivered within 5 seconds | Decision Engine running. Notification Orchestrator running. Twilio/FCM test mode enabled. Customer has registered mobile number. | 1. Inject a pre-scored transaction with `fraud_score: 0.65` (SOFT_DECLINE tier). 2. Consume the decision from `transactions.decisions`. 3. Record decision timestamp. 4. Monitor Notification Gateway for OTP delivery. 5. Record delivery timestamp. | Decision is `SOFT_DECLINE`. OTP notification delivered to registered mobile number within 5 seconds of decision timestamp. OTP is 6 digits. Redis contains an entry for `transaction_id` with 120-second TTL. | - | - |
| **TC-008** | FR-11 | UC4 | HARD_BLOCK decision triggers customer notification within 10 seconds | Notification Orchestrator running. Twilio/FCM test mode enabled. Customer has registered push notification token. | 1. Inject a HARD_BLOCK decision event to `transactions.decisions`. 2. Record the decision timestamp. 3. Monitor FCM test mode for notification delivery. 4. Record delivery timestamp. | Push notification delivered within 10 seconds of decision event. Notification content is human-readable (no raw field names, no fraud score exposed). Notification includes a link to the dispute portal. | - | - |
| **TC-009** | FR-12 | UC7 | Customer successfully submits a dispute for a HARD_BLOCKED transaction | Customer Dispute Portal running. A HARD_BLOCK decision record exists in PostgreSQL for `transaction_id: TXN-TEST-001` dated within 30 days. No prior dispute for this transaction. | 1. Authenticate as the customer via OAuth2. 2. POST to `/v1/disputes` with body `{"transaction_id": "TXN-TEST-001", "note": "This was my own purchase"}`. 3. Inspect the HTTP response. 4. Check PostgreSQL for the dispute record. | HTTP 201 response with `dispute_id` (UUID) and `estimated_resolution: 48 hours`. Dispute record exists in PostgreSQL with `status: OPEN`. Case record created or updated in Case Management Service. | - | - |
| **TC-010** | FR-15 | UC11 | Audit report for a date range contains integrity-verified records for all decision types | Audit Service running. PostgreSQL contains audit records for the past 7 days. HMAC signing key available. | 1. Authenticate as Compliance Officer. 2. POST to `/v1/audit/reports` with date range covering the past 7 days and filter `ALL`. 3. Download the generated report. 4. Inspect report contents. | Report contains records for APPROVE, SOFT_DECLINE, and HARD_BLOCK decisions. Every record has `integrity_status: VERIFIED`. No records show `TAMPERED`. Report metadata includes report generation timestamp and requesting actor ID. | - | - |

---

## 3. Non-Functional Test Scenarios

### NFR-Test-001: Performance - End-to-End Fraud Decision Latency Under Peak Load

**Requirement:** NFR-P1 - End-to-end fraud decision latency shall not exceed 100ms at P99 under 10,000 TPS

**Test Objective:** Verify that the complete SentinelPay pipeline - from Kafka ingestion to decision publication - meets the 100ms P99 latency target when operating at the defined peak load of 10,000 transactions per second.

**Test Type:** Performance / Load Test

**Tools:** Apache JMeter (Kafka producer load injection), OpenTelemetry distributed tracing, Grafana dashboard

**Pre-conditions:**
- All SentinelPay services deployed and healthy on a Kubernetes cluster with minimum replica counts (Ingestion: 3, Feature Engineering: 3, ML Scoring: 5, Decision Engine: 3)
- All ML models loaded in the ML Scoring Service
- Redis cluster populated with behavioural profiles for test accounts
- OpenTelemetry tracing enabled across all services with trace spans from Kafka consumer offset to Kafka producer acknowledgement
- Grafana dashboard configured to display real-time P50, P95, and P99 latency histograms

**Test Procedure:**
1. Run a 5-minute warm-up phase at 1,000 TPS to stabilise caches and JVM JIT compilation
2. Ramp transaction throughput to 5,000 TPS over 2 minutes
3. Ramp to 10,000 TPS over a further 2 minutes
4. Sustain 10,000 TPS for a continuous 30-minute period
5. Capture OpenTelemetry trace data for all transactions during the sustained phase
6. Compute P50, P95, and P99 end-to-end latency from trace span data
7. Capture Kafka consumer lag metrics throughout the test

**Pass Criteria:**

| Metric | Target | Pass / Fail |
|---|---|---|
| P50 end-to-end latency | <= 40ms | - |
| P95 end-to-end latency | <= 80ms | - |
| P99 end-to-end latency | <= 100ms | - |
| Transaction throughput sustained | 10,000 TPS for 30 minutes | - |
| Message loss | 0 messages lost | - |
| Kafka consumer lag | <= 500 messages at all times | - |
| ML Scoring Service error rate | < 0.1% | - |

**Failure Scenarios to Capture:**
- If P99 exceeds 100ms: identify which pipeline stage (ingestion, feature engineering, scoring, or decision) is the bottleneck using trace span breakdown
- If consumer lag grows unbounded: check ML Scoring Service replica count and trigger HPA scale-out
- If error rate exceeds 0.1%: check circuit breaker state and model health

**Expected Result:** All pass criteria met simultaneously during the 30-minute sustained load period. The system demonstrates linear scalability - latency remains stable as throughput increases from 5,000 to 10,000 TPS through horizontal pod autoscaling.

---

### NFR-Test-002: Security - Authentication and Authorisation Enforcement

**Requirement:** NFR-S2 - All external-facing REST API endpoints secured with OAuth 2.0 / JWT. RBAC enforced so that roles cannot access endpoints outside their permission scope.

**Test Objective:** Verify that SentinelPay's API Gateway correctly enforces authentication and role-based access control across all three user roles (Bank Customer, Fraud Analyst, Platform Administrator) and that no cross-role or unauthenticated access is possible.

**Test Type:** Security Test

**Tools:** Postman (API testing), OWASP ZAP (automated security scanning), manual penetration testing

**Pre-conditions:**
- Kong API Gateway running with OAuth 2.0 / JWT plugin configured
- Three test JWT tokens prepared: one for Bank Customer role, one for Fraud Analyst role, one for Platform Administrator role
- One expired JWT token prepared
- One malformed JWT token prepared

**Test Procedure and Expected Results:**

| Sub-Test | Token Used | Endpoint Tested | Expected HTTP Response | Pass / Fail |
|---|---|---|---|---|
| ST-001: No token | None | `GET /v1/cases` | 401 Unauthorized | - |
| ST-002: Expired token | Expired JWT | `GET /v1/cases` | 401 Unauthorized | - |
| ST-003: Malformed token | Malformed JWT (invalid signature) | `GET /v1/cases` | 401 Unauthorized | - |
| ST-004: Customer accesses analyst endpoint | Customer JWT | `GET /v1/cases` | 403 Forbidden | - |
| ST-005: Customer accesses own dispute | Customer JWT | `GET /v1/disputes/{own_dispute_id}` | 200 OK with own data | - |
| ST-006: Customer accesses other customer's dispute | Customer JWT | `GET /v1/disputes/{other_customer_dispute_id}` | 403 Forbidden | - |
| ST-007: Analyst accesses case queue | Analyst JWT | `GET /v1/cases` | 200 OK with case list | - |
| ST-008: Analyst accesses admin config endpoint | Analyst JWT | `PUT /v1/admin/thresholds` | 403 Forbidden | - |
| ST-009: Admin accesses threshold config | Admin JWT | `PUT /v1/admin/thresholds` | 200 OK | - |
| ST-010: Admin accesses case queue | Admin JWT | `GET /v1/cases` | 403 Forbidden (admin does not have analyst role) | - |
| ST-011: Token replay after expiry | Valid but expired Customer JWT | `POST /v1/disputes` | 401 Unauthorized | - |
| ST-012: SQL injection in dispute note field | Customer JWT | `POST /v1/disputes` with `note: "'; DROP TABLE disputes;--"` | 201 OK (note stored as escaped string, no SQL executed) | - |

**Pass Criteria:**
- All 12 sub-tests produce the expected HTTP response code
- Zero successful unauthorised access attempts
- Customer account data isolation: no Customer JWT can retrieve another customer's data
- SQL injection attempt produces no database side effects (verified by checking dispute table row count before and after)
- OWASP ZAP automated scan produces zero Critical or High severity findings against the API Gateway

**Expected Result:** All sub-tests pass. The API Gateway correctly enforces authentication on every request, returns 401 for missing/invalid/expired tokens, returns 403 for valid tokens accessing out-of-scope endpoints, and enforces customer data isolation through account token binding in JWT claims.

---

## 4. Test Traceability Matrix

| Test Case ID | Requirement | Use Case | Test Type | Priority |
|---|---|---|---|---|
| TC-001 | FR-01 | UC1 | Functional - Integration | Critical |
| TC-002 | FR-02 | UC1 | Functional - Negative | Critical |
| TC-003 | FR-03 | UC1 | Functional - Security | Critical |
| TC-004 | FR-04 | UC3 | Functional - Integration | Critical |
| TC-005 | FR-06 | UC4 | Functional - Integration | High |
| TC-006 | FR-07 | UC4 | Functional - Integration | Critical |
| TC-007 | FR-08 | UC5 | Functional - Integration | Critical |
| TC-008 | FR-11 | UC4 | Functional - Integration | High |
| TC-009 | FR-12 | UC7 | Functional - Integration | High |
| TC-010 | FR-15 | UC11 | Functional - Integration | Critical |
| NFR-Test-001 | NFR-P1 | UC3, UC4 | Performance - Load | Critical |
| NFR-Test-002 | NFR-S2 | UC7, UC8, UC11 | Security - Penetration | Critical |

---

*SentinelPay TEST_CASES.md - Version 1.0 | March 2026*
*Assignment 5 - Builds on Assignments 3 and 4*