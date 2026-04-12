# AGILE_PLANNING.md - Agile User Stories, Backlog, and Sprint Planning
## SentinelPay: Real-Time Fraud Detection & Prevention Engine

> **Assignment 6 - Agile Planning Document**
> Methodology: Scrum | Sprint Duration: 2 Weeks
> Builds directly on Assignment 4 (SRD.md) and Assignment 5 (USE_CASE_SPECIFICATIONS.md)

---

## 1. Agile Context

SentinelPay is transitioning from specification and architecture (Assignments 3-5) into active Agile development. This document captures the product backlog, sprint planning, and user stories that will drive the first development iteration toward a Minimum Viable Product (MVP).

**Scrum Roles (solo project context):**
- **Product Owner:** Teboho Mokoni - prioritises backlog based on stakeholder value
- **Scrum Master:** Teboho Mokoni - facilitates the sprint and removes blockers
- **Developer:** Teboho Mokoni - implements all tasks

**MVP Definition:** A working fraud detection pipeline that can ingest a transaction, score it using a basic ML model, make an approve/block decision, persist the decision to the database, and return the result - all within the 100ms latency target.

---

## 2. User Stories

User stories are derived from functional requirements in SRD.md and use cases in USE_CASE_SPECIFICATIONS.md. Every story follows the format: *"As a [role], I want [action] so that [benefit]."* All stories satisfy the INVEST criteria (Independent, Negotiable, Valuable, Estimable, Small, Testable).

### 2.1 User Story Table

| Story ID | User Story | Acceptance Criteria | Priority |
|---|---|---|---|
| **US-001** | As a **Payment Processor**, I want to publish transaction events to a Kafka topic so that SentinelPay can evaluate them for fraud in real time. *(Traces to: FR-01, UC1)* | Transaction events consumed from `transactions.raw` within 5ms at P99. System sustains 10,000 events/sec for 60 minutes without message loss. Consumer group rebalancing completes within 10 seconds. | High |
| **US-002** | As a **Payment Processor**, I want malformed transaction payloads to be automatically rejected and routed to a dead-letter queue so that bad data never reaches the fraud scoring pipeline. *(Traces to: FR-02, UC1)* | Events missing mandatory fields are dead-lettered within 2ms with error code and specific failed field identified. 100% of rejected events produce a structured log entry. | High |
| **US-003** | As a **Compliance Officer**, I want all PII fields tokenised at the ingestion boundary so that raw account numbers and device fingerprints never appear in the ML pipeline or audit logs. *(Traces to: FR-03, UC1)* | Downstream Kafka topics contain zero raw PII values. Tokenisation adds ≤3ms to ingestion time at P99. Automated quarterly PII scan produces zero findings. | High |
| **US-004** | As a **Fraud Analyst**, I want every transaction scored by an ML ensemble so that fraud decisions are based on multiple independent signals rather than a single model that can be gamed. *(Traces to: FR-04, FR-05, UC3)* | Every scored result contains `fraud_score` (0.0-1.0), `risk_tier` (LOW/MEDIUM/HIGH/CRITICAL), and `model_version_composite`. Ensemble scoring completes within 60ms at P99. | High |
| **US-005** | As a **Bank Customer**, I want suspicious transactions to trigger a step-up authentication challenge rather than being immediately blocked so that I can prove my identity and complete legitimate purchases. *(Traces to: FR-08, UC5)* | Step-up OTP delivered within 5 seconds of SOFT_DECLINE. Successful OTP results in APPROVE within 2 seconds. Challenge timeout of 120 seconds enforced. | High |
| **US-006** | As a **Bank Customer**, I want to receive an instant push notification or SMS when a transaction is blocked so that I know immediately and can take action. *(Traces to: FR-11, UC4)* | Notification delivered within 10 seconds of HARD_BLOCK at P95. Content is human-readable with no raw technical fields. Notification includes dispute portal link. | High |
| **US-007** | As a **Bank Customer**, I want to formally dispute a blocked transaction through the app so that I have a clear process to challenge incorrect fraud decisions. *(Traces to: FR-12, UC7)* | `POST /v1/disputes` returns HTTP 201 with `dispute_id` within 1 second. Dispute persisted in PostgreSQL. Fraud analyst queue notified within 60 seconds. | Medium |
| **US-008** | As a **Fraud Analyst**, I want to see a prioritised queue of fraud cases with SHAP explanations so that I can quickly understand why each transaction was flagged and make a confident resolution decision. *(Traces to: FR-09, FR-10, UC8)* | Case queue loads within 2 seconds. Each case displays top 5 SHAP features in human-readable labels. Resolution persisted within 1 second of analyst submission. | High |
| **US-009** | As a **Fraud Analyst**, I want confirmed fraud cases to automatically feed into the ML retraining pipeline so that the model improves over time from my investigation decisions. *(Traces to: FR-13, UC10)* | CONFIRMED_FRAUD resolution publishes labelled sample to `fraud.labels` topic within 60 seconds. Retraining triggered automatically when buffer reaches 500 samples. | Medium |
| **US-010** | As a **ML Engineer**, I want new model versions to be hot-swapped into the scoring service without restarting it so that model improvements are deployed with zero downtime and no dropped transactions. *(Traces to: FR-14, UC10)* | Hot-swap completes within 5 seconds of new Production model detected in MLflow. Zero scoring requests dropped during swap. Swap event logged with old and new version details. | Medium |
| **US-011** | As a **Compliance Officer**, I want every fraud decision logged in a tamper-evident audit trail so that I can produce a verifiable record of system activity for regulatory examinations. *(Traces to: FR-15, UC11)* | Audit record written synchronously before decision response returned. Records include HMAC-SHA256 `record_hash`. Any tampered record detected by daily integrity check within 24 hours. | High |
| **US-012** | As a **Platform Administrator**, I want all services to emit Prometheus metrics and structured logs so that I can detect performance degradation and incidents within 2 minutes of occurrence. *(Traces to: NFR-O1, UC12)* | All services expose `/metrics` endpoint. Grafana dashboard shows P50/P95/P99 latency in real time. Alert fires within 2 minutes of P99 exceeding 100ms. | Medium |
| **US-013** | As a **System Administrator**, I want all inter-service communication encrypted with mTLS so that security compliance is maintained and no unencrypted traffic flows inside the cluster. *(Traces to: NFR-S1)* | Network traffic scan detects zero unencrypted inter-service connections. TLS version audit confirms no TLS 1.2 or below connections accepted. | Medium |
| **US-014** | As a **Fraud Analyst**, I want configurable fraud detection rule thresholds per account tier so that the system balances fraud catch rate against false positive rate differently for Standard, Premium, and Business customers. *(Traces to: FR-06, FR-07, UC4)* | Threshold changes applied via Admin API within 60 seconds without service restart. Decision output includes `threshold_applied` and `account_tier` fields. Rule changes logged in audit trail. | Low |

---

### 2.2 INVEST Criteria Verification

All 14 user stories are evaluated against the INVEST criteria. The table below demonstrates compliance using US-004 as the representative example, with notes on how all stories meet each criterion.

| Criteria | How US-004 (ML Ensemble Scoring) Satisfies It | Applied Across All Stories |
|---|---|---|
| **Independent** | Scoring service is a standalone Python microservice consuming from Kafka - deployable without any other story being complete | Each story maps to a distinct service or API boundary |
| **Negotiable** | The model weights (XGBoost 60%, IF 25%, BERT 15%) can be adjusted based on validation results without changing the story's value | Implementation details in all stories are open to negotiation |
| **Valuable** | Directly addresses the core business problem - fraud detection accuracy is the primary value proposition of SentinelPay | Every story is traced to a specific stakeholder concern from STAKEHOLDER_ANALYSIS.md |
| **Estimable** | Clear scope: FastAPI service, three model loaders, ensemble aggregator, Kafka consumer/producer | All stories have defined acceptance criteria that bound the scope |
| **Small** | Scoped to a single service - does not include UI, notification, or case management | Stories with large scope (US-004) are limited to one container from ARCHITECTURE.md |
| **Testable** | TC-004 in TEST_CASES.md defines exact acceptance criteria including latency targets and output field requirements | Every story has measurable acceptance criteria that map to test cases in Assignment 5 |

---

## 3. Product Backlog

The product backlog organises all 14 user stories using MoSCoW prioritisation. Story points follow the Fibonacci sequence (1, 2, 3, 5, 8, 13) where 1-2 points = simple/well-understood, 3-5 = moderate complexity with integration work, 8-13 = high complexity spanning multiple services with significant testing required.

### 3.1 Backlog Table

| Story ID | User Story | Priority (MoSCoW) | Effort Estimate (Points) | Dependencies |
|---|---|---|---|---|
| **US-001** | As a Payment Processor, I want to publish transaction events to a Kafka topic so that SentinelPay can evaluate them for fraud in real time. | Must-have | 3 | None - this is the pipeline foundation |
| **US-002** | As a Payment Processor, I want malformed transaction payloads to be automatically rejected and routed to a dead-letter queue so that bad data never reaches the fraud scoring pipeline. | Must-have | 2 | US-001 (Kafka topic must exist first) |
| **US-003** | As a Compliance Officer, I want all PII fields tokenised at the ingestion boundary so that raw account numbers and device fingerprints never appear in the ML pipeline or audit logs. | Must-have | 5 | US-001, US-002 (runs within the ingestion service) |
| **US-004** | As a Fraud Analyst, I want every transaction scored by an ML ensemble so that fraud decisions are based on multiple independent signals rather than a single model that can be gamed. | Must-have | 13 | US-001, US-002, US-003 (requires enriched events) |
| **US-005** | As a Bank Customer, I want suspicious transactions to trigger a step-up authentication challenge rather than being immediately blocked so that I can prove my identity and complete legitimate purchases. | Must-have | 8 | US-004, US-006 (needs decision and notification working) |
| **US-006** | As a Bank Customer, I want to receive an instant push notification or SMS when a transaction is blocked so that I know immediately and can take action. | Must-have | 5 | US-004 (decision must exist before notification) |
| **US-011** | As a Compliance Officer, I want every fraud decision logged in a tamper-evident audit trail so that I can produce a verifiable record of system activity for regulatory examinations. | Must-have | 5 | US-004 (needs decisions to log) |
| **US-008** | As a Fraud Analyst, I want to see a prioritised queue of fraud cases with SHAP explanations so that I can quickly understand why each transaction was flagged and make a confident resolution decision. | Should-have | 8 | US-004, US-011 (cases derived from decisions and audit) |
| **US-007** | As a Bank Customer, I want to formally dispute a blocked transaction through the app so that I have a clear process to challenge incorrect fraud decisions. | Should-have | 5 | US-006 (customer must have received the block notification) |
| **US-009** | As a Fraud Analyst, I want confirmed fraud cases to automatically feed into the ML retraining pipeline so that the model improves over time from my investigation decisions. | Should-have | 8 | US-008 (analyst must be able to resolve cases first) |
| **US-012** | As a Platform Administrator, I want all services to emit Prometheus metrics and structured logs so that I can detect performance degradation and incidents within 2 minutes of occurrence. | Should-have | 5 | US-001 through US-006 (services must exist to emit metrics) |
| **US-010** | As a ML Engineer, I want new model versions to be hot-swapped into the scoring service without restarting it so that model improvements are deployed with zero downtime and no dropped transactions. | Could-have | 8 | US-004, US-009 (scoring and retraining must both work) |
| **US-013** | As a System Administrator, I want all inter-service communication encrypted with mTLS so that security compliance is maintained and no unencrypted traffic flows inside the cluster. | Could-have | 5 | All application services deployed and stable |
| **US-014** | As a Fraud Analyst, I want configurable fraud detection rule thresholds per account tier so that the system balances fraud catch rate against false positive rate differently for Standard, Premium, and Business customers. | Won't-have (Sprint 1) | 3 | US-004 (scoring must be working with default thresholds first) |

**Total backlog story points: 83**
**Sprint 1 capacity (2 weeks, solo developer): 33 points**

---

### 3.2 Prioritisation Justification

**Must-have stories (US-001, US-002, US-003, US-004, US-005, US-006, US-011)** represent the irreducible core of SentinelPay. Without these seven stories the system cannot perform its fundamental purpose - detecting and responding to fraud in real time. They map directly to the MVP definition and address the highest-influence stakeholders from STAKEHOLDER_ANALYSIS.md: the Payment Processor needs reliable ingestion (US-001, US-002), the Bank Customer needs protection and notification (US-004, US-005, US-006), and the Compliance Officer needs an audit trail from day one (US-003, US-011). These stories collectively address the Bank Customer's success metric of "fraud detected before settlement in ≥95% of cases."

**Should-have stories (US-007, US-008, US-009, US-012)** add significant operational and analytical value but the system can demonstrate core fraud detection without them in Sprint 1. The analyst case queue (US-008) and retraining pipeline (US-009) are what make SentinelPay improve over time rather than remaining static - they are critical for long-term accuracy but not for proving the pipeline works. US-007 (dispute API) and US-012 (observability) are important for production readiness but not for MVP demonstration.

**Could-have stories (US-010, US-013)** are architectural quality improvements. Zero-downtime hot-swap (US-010) and mTLS encryption (US-013) make the system production-grade but the core fraud detection function operates correctly without them in a development environment.

**Won't-have in Sprint 1 (US-014):** Configurable per-tier thresholds require a working Admin API with proper authentication, configuration persistence, and real-time threshold propagation. Default thresholds applied uniformly across all account tiers are sufficient to prove the decision engine works during Sprint 1. This story is explicitly deferred to Sprint 2.

---

## 4. Sprint Planning

### 4.1 Sprint 1 Goal

> *"Implement the core SentinelPay fraud detection pipeline - from Kafka transaction ingestion through ML ensemble scoring to automated approve/block decision and customer notification - with full audit logging. By the end of Sprint 1, a transaction published to `transactions.raw` shall travel through the complete pipeline and produce a persisted, audited fraud decision within 100ms."*

This sprint delivers the MVP by implementing all Must-have stories except US-005 (step-up auth, deferred to Sprint 2 due to dependency complexity). It proves the core architecture decision from ARCHITECTURE.md - that an event-driven Kafka pipeline can achieve sub-100ms fraud detection - and gives every stakeholder a tangible demonstration of the system working.

**Stories Selected for Sprint 1:**

| Story ID | User Story | Story Points |
|---|---|---|
| US-001 | As a Payment Processor, I want to publish transaction events to a Kafka topic... | 3 |
| US-002 | As a Payment Processor, I want malformed payloads dead-lettered automatically... | 2 |
| US-003 | As a Compliance Officer, I want all PII fields tokenised at ingestion... | 5 |
| US-004 | As a Fraud Analyst, I want every transaction scored by an ML ensemble... | 13 |
| US-006 | As a Bank Customer, I want to receive an instant notification when blocked... | 5 |
| US-011 | As a Compliance Officer, I want every decision logged in a tamper-evident audit trail... | 5 |
| **Total** | | **33 points** |

> **Note on US-005 deferral:** Step-up authentication depends on US-006 (notification) being stable and adds OTP generation, Redis TTL management, and a challenge-response API. Adding this to Sprint 1 would push the sprint to 41 points, exceeding solo developer capacity. It is the first story in Sprint 2.

---

### 4.2 Sprint Backlog Table

| Task ID | Task Description | Assigned To | Estimated Hours | Status |
|---|---|---|---|---|
| **T-001** | Set up Kafka broker and create all 9 required topics via Docker Compose | Teboho | 3 | To Do |
| **T-002** | Implement Kafka consumer in Ingestion Service (Spring Boot) - subscribe to `transactions.raw` with consumer group | Teboho | 5 | To Do |
| **T-003** | Implement Kafka producer in Ingestion Service - publish validated events to `transactions.enriched` | Teboho | 3 | To Do |
| **T-004** | Write integration test TC-001: verify ingestion latency ≤5ms at P99 | Teboho | 3 | To Do |
| **T-005** | Implement JSON schema validator - check all 11 mandatory fields per FR-02 | Teboho | 4 | To Do |
| **T-006** | Implement dead-letter queue producer - route rejected events to `transactions.dlq` with structured error payload | Teboho | 3 | To Do |
| **T-007** | Write negative test TC-002: verify missing `amount` field causes dead-letter with `SCHEMA_VALIDATION_FAILED` | Teboho | 2 | To Do |
| **T-008** | Implement PII tokenisation component - tokenise `account_id`, `device_fingerprint`, `ip_address` via token vault | Teboho | 5 | To Do |
| **T-009** | Write test TC-003: verify zero raw PII values in `transactions.enriched` payload | Teboho | 2 | To Do |
| **T-010** | Implement threat intelligence enrichment - add known bad IP/BIN flags to enriched payload | Teboho | 4 | To Do |
| **T-011** | Set up Python FastAPI scoring service skeleton with Kafka consumer and producer | Teboho | 4 | To Do |
| **T-012** | Implement feature engineering: velocity counters in Redis, geo-deviation score, 30-day amount baseline from Cassandra | Teboho | 8 | To Do |
| **T-013** | Train baseline XGBoost model on IEEE-CIS Fraud Detection dataset and register in MLflow as Production | Teboho | 6 | To Do |
| **T-014** | Implement Isolation Forest anomaly scorer | Teboho | 4 | To Do |
| **T-015** | Implement Ensemble Aggregator - weighted average of three model scores, risk tier mapping | Teboho | 5 | To Do |
| **T-016** | Implement Model Loader - load Production model from MLflow on startup, poll for updates every 60 seconds | Teboho | 4 | To Do |
| **T-017** | Write test TC-004: verify scored result contains `fraud_score`, `risk_tier`, `model_version_composite` | Teboho | 2 | To Do |
| **T-018** | Write performance test: verify scoring completes within 60ms at P99 under 1,000 TPS | Teboho | 3 | To Do |
| **T-019** | Implement Decision Engine (Spring Boot) - consume scored events, apply thresholds, produce APPROVE/SOFT_DECLINE/HARD_BLOCK | Teboho | 6 | To Do |
| **T-020** | Implement decision persistence - write decision record to PostgreSQL `fraud_decisions` table | Teboho | 3 | To Do |
| **T-021** | Implement Notification Orchestrator - consume HARD_BLOCK events, dispatch to Twilio test mode | Teboho | 5 | To Do |
| **T-022** | Write test TC-008: verify notification delivered within 10 seconds of HARD_BLOCK event | Teboho | 2 | To Do |
| **T-023** | Implement Audit Service - consume all decision events from `audit.events`, write records to PostgreSQL | Teboho | 5 | To Do |
| **T-024** | Implement HMAC-SHA256 record hash generation and storage per FR-15 | Teboho | 3 | To Do |
| **T-025** | Write test TC-010: verify audit record exists for APPROVE, SOFT_DECLINE, and HARD_BLOCK decisions | Teboho | 2 | To Do |
| **T-026** | End-to-end integration test: publish transaction to `transactions.raw`, verify persisted audited decision in PostgreSQL within 100ms | Teboho | 4 | To Do |
| **T-027** | Update DOCKER.md with Sprint 1 service changes and verify Docker Compose stack starts cleanly | Teboho | 1 | To Do |

**Total estimated hours: 111 hours**
**Sprint duration: 2 weeks = 10 working days**
**Daily capacity (solo): ~11 hours/day**

---

### 4.3 Sprint 1 Definition of Done

A user story is considered Done when all of the following are true:
- [ ] All acceptance criteria from the user story table are met and verifiable
- [ ] All associated tasks are marked complete in the GitHub Project board
- [ ] Code is committed and pushed to the `main` branch with a meaningful commit message
- [ ] All associated test cases from TEST_CASES.md pass without errors
- [ ] No new critical bugs introduced anywhere in the pipeline
- [ ] Docker Compose stack starts cleanly with the new service included and healthy

---

### 4.4 Sprint 1 Burndown Plan

| Day | Points Remaining | Stories in Progress |
|---|---|---|
| Day 1 | 33 | US-001: T-001 (Kafka infrastructure) |
| Day 2 | 30 | US-001: T-002, T-003, T-004 complete |
| Day 3 | 28 | US-002: T-005, T-006, T-007 complete |
| Day 4 | 23 | US-003: T-008, T-009, T-010 complete |
| Day 5 | 20 | US-004: T-011, T-012 in progress |
| Day 6 | 20 | US-004: T-012, T-013 in progress (model training) |
| Day 7 | 10 | US-004: T-014, T-015, T-016, T-017, T-018 complete |
| Day 8 | 5 | US-006: T-019, T-020, T-021, T-022 complete |
| Day 9 | 0 | US-011: T-023, T-024, T-025 complete |
| Day 10 | 0 | T-026, T-027: integration testing and documentation |

---

## 5. GitHub Agile Tools - Setup Record

The following GitHub tools are used to manage this sprint. The marker can verify these at `https://github.com/Teboho66/SentinelPay`.

### GitHub Issues
One issue created per user story. Each issue follows this structure:
- **Title:** `[US-XXX] Short story summary`
- **Labels:** `user-story`, `must-have` / `should-have` / `could-have`, `sprint-1` (where applicable)
- **Body:** Full user story text, acceptance criteria checklist, traceability (FR/UC references), story points
- **Milestone:** Sprint 1 - Core Pipeline MVP

### GitHub Milestone
- **Name:** `Sprint 1 - Core Pipeline MVP`
- **Due date:** 2 weeks from sprint start
- **Description:** Implement end-to-end fraud detection pipeline from Kafka ingestion to decision and audit logging within 100ms

### GitHub Project Board
- **Name:** `SentinelPay Sprint Board`
- **View:** Board (Kanban)
- **Columns:** `Backlog` | `Sprint 1 - To Do` | `In Progress` | `Done`
- All 14 user story issues added to the board
- Sprint 1 stories (US-001 to US-004, US-006, US-011) moved to `Sprint 1 - To Do`

### Issue Labels to Create
Go to `Issues → Labels → New Label` and create:
- `user-story` (blue)
- `must-have` (red)
- `should-have` (orange)
- `could-have` (yellow)
- `sprint-1` (green)
- `nfr` (purple)

---

## 6. Full Traceability Matrix

| Story ID | Assignment 4 FR/NFR | Assignment 5 UC | Assignment 5 TC | Stakeholder (from A4) |
|---|---|---|---|---|
| US-001 | FR-01 | UC1 | TC-001 | Payment Processor Integration Team |
| US-002 | FR-02 | UC1 | TC-002 | Payment Processor, Compliance Officer |
| US-003 | FR-03 | UC1 | TC-003 | Compliance Officer, Financial Regulator |
| US-004 | FR-04, FR-05 | UC3 | TC-004 | Fraud Analyst, ML Engineer |
| US-005 | FR-08 | UC5 | TC-007 | Bank Customer, Compliance Officer |
| US-006 | FR-11 | UC4 | TC-008 | Bank Customer |
| US-007 | FR-12 | UC7 | TC-009 | Bank Customer, Fraud Analyst |
| US-008 | FR-09, FR-10 | UC8 | - | Fraud Analyst, Compliance Officer |
| US-009 | FR-13 | UC10 | - | ML Engineer, Executive Leadership |
| US-010 | FR-14 | UC10 | - | ML Engineer, Platform Administrator |
| US-011 | FR-15 | UC11 | TC-010 | Compliance Officer, Financial Regulator |
| US-012 | NFR-O1 | UC12 | NFR-Test-001 | Platform Administrator |
| US-013 | NFR-S1 | - | NFR-Test-002 | Compliance Officer |
| US-014 | FR-06, FR-07 | UC4 | TC-005, TC-006 | Platform Admin, Fraud Analyst |

---

