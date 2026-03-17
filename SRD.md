# SRD.md - System Requirements Document
## SentinelPay: Real-Time Fraud Detection & Prevention Engine

> **Assignment 4 - System Requirements Document**
> Version: 2.0 | Date: March 2026
> Building on Assignment 3 | Status: Active

---

## 1. Document Purpose

This System Requirements Document (SRD) defines the complete functional and non-functional requirements for SentinelPay. It builds directly on the system specification established in Assignment 3 and extends it with stakeholder-traced, acceptance-criteria-backed requirements elicited through structured stakeholder analysis.

Every requirement in this document is:
- **Specific** - states precisely what the system shall do or achieve
- **Measurable** - includes quantifiable acceptance criteria
- **Traceable** - linked to the stakeholder concern it addresses
- **Unambiguous** - uses "shall" for mandatory requirements throughout

---

## 2. System Overview

**System Name:** SentinelPay - Real-Time Fraud Detection & Prevention Engine

**Domain:** FinTech - Digital Payments & Financial Crime Prevention

**Problem Statement:** Financial institutions require sub-100ms fraud decisions on millions of daily transactions across instant payment rails. Legacy batch-processing and rule-only systems cannot adapt to AI-assisted fraud patterns at the speed modern payment infrastructure demands. SentinelPay delivers a real-time, continuously-learning fraud intelligence platform using an event-driven microservices architecture and an ML ensemble engine.

**System Boundary:** SentinelPay covers transaction ingestion from payment processors, real-time ML-based fraud scoring, automated decision enforcement, fraud case management, customer notification and dispute handling, regulatory audit logging, and continuous ML model retraining. Production cloud deployment and direct licensed payment network participation are out of scope for this academic specification.

---

## 3. Functional Requirements

Functional requirements define what the system shall do - its capabilities and behaviours. Each requirement below includes a unique identifier, a stakeholder traceability reference, the requirement statement, and measurable acceptance criteria.

---

### FR Category 1: Transaction Ingestion and Validation

---

#### FR-01 - Real-Time Transaction Event Ingestion

**Stakeholder:** Payment Processor Integration Team, Executive Leadership

**Requirement:**
The system shall ingest financial transaction events in real time from external payment processors via a dedicated Apache Kafka topic (`transactions.raw`), supporting a sustained throughput of at least 10,000 transaction events per second.

**Acceptance Criteria:**
- Transaction events are consumed from the `transactions.raw` Kafka topic within 5ms of publication at P99 under normal load
- The system sustains 10,000 events/second throughput for a continuous 60-minute period without message loss or consumer lag exceeding 500 messages
- Consumer group rebalancing on service restart completes within 10 seconds without duplicate processing of already-committed offsets

---

#### FR-02 - Transaction Payload Schema Validation

**Stakeholder:** Payment Processor Integration Team, Compliance Officer

**Requirement:**
The system shall validate every ingested transaction event against a versioned JSON schema. The schema shall require the following mandatory fields: `transaction_id`, `account_id`, `merchant_id`, `merchant_category_code`, `amount`, `currency`, `timestamp`, `channel`, `device_fingerprint_token`, `ip_address_hash`, and `geolocation`.

**Acceptance Criteria:**
- Events missing any mandatory field are rejected within 2ms of consumption and routed to the `transactions.dlq` dead-letter queue
- Events with invalid field types (e.g., non-numeric amount, invalid ISO 8601 timestamp) are rejected and dead-lettered with a structured error payload indicating the specific failed validation rule
- Schema validation logic is version-controlled and the active schema version is included in all enriched event payloads downstream
- 100% of dead-lettered events produce a structured error log entry retrievable via the observability stack

---

#### FR-03 - PII Tokenisation at Ingestion Boundary

**Stakeholder:** Compliance Officer, Financial Regulator

**Requirement:**
The system shall tokenise all Personally Identifiable Information (PII) fields - specifically `account_id`, `device_fingerprint`, and raw `ip_address` - at the Transaction Ingestion Service boundary before any downstream publication. Raw PII values shall never be published to Kafka topics or persisted in the feature store, ML training data, or audit logs.

**Acceptance Criteria:**
- All downstream Kafka topics contain only tokenised references (e.g., `acc_token_xxxx`, `dfp_token_xxxx`) - never raw account numbers or device identifiers
- Automated quarterly PII scan of all Kafka topics, feature store, and PostgreSQL fraud_decisions table produces zero raw PII findings
- Token-to-PII resolution is only possible via the secure token vault service, which requires elevated authorisation
- Tokenisation adds ≤ 3ms to ingestion processing time at P99

---

### FR Category 2: Fraud Scoring and Detection

---

#### FR-04 - ML Ensemble Fraud Scoring

**Stakeholder:** Fraud Analyst, ML Engineer, Executive Leadership

**Requirement:**
The system shall score every validated and enriched transaction event using a multi-model ML ensemble consisting of: (1) an XGBoost gradient boosting classifier trained on tabular transaction features, (2) an Isolation Forest unsupervised anomaly detector, and (3) a fine-tuned DistilBERT sequence classifier for merchant text analysis. The ensemble shall produce a composite `fraud_score` value between 0.0 and 1.0 and a `risk_tier` classification of LOW, MEDIUM, HIGH, or CRITICAL.

**Acceptance Criteria:**
- Every scored transaction includes `fraud_score` (float, 4 decimal places), `risk_tier` (enum), `model_version_composite` (string), and `processing_ms` (integer) in the output payload
- Ensemble scoring completes within 60ms at P99 as measured from feature vector receipt to score publication on `transactions.scored` Kafka topic
- All three sub-models execute; if any single sub-model fails, the circuit breaker activates fallback scoring using the remaining models and logs a degraded-mode alert
- Composite model version string includes the version of each constituent model (e.g., `xgb-v3.1|iso-v2.0|bert-v1.4`)

---

#### FR-05 - Behavioural Profile-Based Feature Enrichment

**Stakeholder:** Fraud Analyst, ML Engineer

**Requirement:**
The system shall enrich every transaction event with real-time behavioural features derived from the transacting account's historical profile. Enrichment shall include: velocity metrics (transaction count in past 1 hour, 6 hours, and 24 hours), average transaction amount deviation from 30-day baseline, geo-velocity score (distance from last known location divided by time elapsed), and device novelty flag (whether the device token has been seen before for this account).

**Acceptance Criteria:**
- Feature enrichment completes within 15ms at P99, querying Redis for velocity counters and Cassandra for 30-day baseline data
- Velocity counters in Redis are updated atomically with each transaction to prevent race conditions
- For new accounts with fewer than 10 historical transactions, the system applies a configurable new-account risk boost to the `fraud_score` output
- Feature vector schema is version-controlled and matches exactly between training and serving environments (zero training-serving skew, enforced by shared Pydantic schema definition)

---

#### FR-06 - Configurable Rule-Based Pre-Filters

**Stakeholder:** Platform Administrator, Fraud Analyst, Compliance Officer

**Requirement:**
The system shall apply configurable rule-based pre-filter checks to every transaction before ML scoring. Pre-filter rules shall include at minimum: merchant blacklist matching, known compromised card token matching against threat intelligence feed data, transaction amount hard limits per account tier, and geographic restriction rules. Pre-filter matches shall produce an immediate HARD_BLOCK decision without invoking the ML scoring pipeline.

**Acceptance Criteria:**
- Pre-filter rule evaluation completes within 5ms at P99
- Rules are configurable via the Admin API without service restart; rule changes take effect within 30 seconds of API confirmation
- Every pre-filter match produces an audit log entry identifying the specific rule triggered
- Blacklist and threat intelligence data is refreshed from the external feed on a configurable schedule (default: every 15 minutes)
- Pre-filter HARD_BLOCK decisions are indistinguishable from ML-based decisions in the customer-facing notification - they appear as a standard decline

---

### FR Category 3: Decision Engine

---

#### FR-07 - Automated Fraud Decision Enforcement

**Stakeholder:** Bank Customer, Payment Processor Integration Team, Fraud Analyst

**Requirement:**
The system shall evaluate the ML ensemble `fraud_score` and `risk_tier` output against configurable per-account-tier decision thresholds and produce a final decision of APPROVE, SOFT_DECLINE, or HARD_BLOCK for every transaction. Decision thresholds shall be independently configurable for Standard, Premium, and Business account tiers.

**Acceptance Criteria:**
- A decision is produced for 100% of scored transactions with no unhandled exceptions
- End-to-end decision latency (from Kafka ingestion to decision publication) ≤ 100ms at P99 under 10,000 TPS load
- Decision threshold configuration is accessible via the Admin API; changes propagate to the Decision Engine within 60 seconds without service restart
- Decision output payload includes: `decision` (enum), `fraud_score`, `risk_tier`, `threshold_applied`, `account_tier`, `rule_triggers` (array), `decided_at` (ISO 8601 timestamp), `processing_ms`

---

#### FR-08 - Step-Up Authentication for SOFT_DECLINE

**Stakeholder:** Bank Customer, Compliance Officer

**Requirement:**
For transactions receiving a SOFT_DECLINE decision, the system shall trigger a step-up authentication challenge to the customer via the Notification Orchestrator. The system shall await a customer authentication response for a configurable timeout period (default: 120 seconds). Successful authentication shall result in the transaction being reprocessed as APPROVE. Timeout or failed authentication shall escalate the decision to HARD_BLOCK.

**Acceptance Criteria:**
- Step-up challenge notification delivered to customer device within 5 seconds of SOFT_DECLINE decision
- Customer authentication response correctly processed within 2 seconds of receipt
- Challenge timeout of 120 seconds is configurable per account tier via Admin API
- 100% of step-up outcomes (success, timeout, failure) are logged in the audit trail with timestamps
- Step-up completion rate (customers who successfully complete the challenge) is tracked as a KPI metric on the operations dashboard

---

### FR Category 4: Case Management

---

#### FR-09 - Automated Fraud Case Generation

**Stakeholder:** Fraud Analyst, Compliance Officer

**Requirement:**
The system shall automatically generate a fraud investigation case for every transaction that receives a HARD_BLOCK decision with a `risk_tier` of HIGH or CRITICAL. Each case shall be created in the Case Management Service within 2 seconds of the decision event and assigned a priority level derived from the `fraud_score` value.

**Acceptance Criteria:**
- 100% of HIGH and CRITICAL HARD_BLOCK decisions result in a case record created in PostgreSQL within 2 seconds
- Case records include: `case_id`, `transaction_id`, `account_id_token`, `fraud_score`, `risk_tier`, `decision`, `shap_report_ref`, `created_at`, `status` (OPEN / IN_REVIEW / CONFIRMED / DISMISSED), `assigned_analyst_id` (nullable), `priority` (P1 / P2 / P3)
- Cases with `fraud_score` ≥ 0.90 are assigned P1 priority and appear at the top of the analyst queue
- Case generation failure triggers an alert to the Platform Administrator within 30 seconds

---

#### FR-10 - Analyst Case Review and Resolution

**Stakeholder:** Fraud Analyst, ML Engineer

**Requirement:**
The system shall provide a fraud analyst dashboard that allows analysts to view the case queue, drill into individual cases, review transaction details and SHAP explanations, and record a resolution decision of CONFIRMED_FRAUD or FALSE_POSITIVE with an optional analyst note. Resolution decisions shall be persisted and trigger downstream actions.

**Acceptance Criteria:**
- Analyst dashboard loads the case queue within 2 seconds of login
- Individual case detail view - including transaction data, account behaviour summary, and SHAP feature importance chart - loads within 3 seconds
- Resolution (CONFIRMED_FRAUD or FALSE_POSITIVE) is persisted within 1 second of analyst submission
- CONFIRMED_FRAUD resolutions automatically publish a labelled fraud sample to the MLOps retraining buffer topic within 60 seconds
- Analyst resolution audit record includes: `analyst_id`, `resolution`, `resolved_at`, `note` (text)
- Dashboard displays analyst SLA indicator showing cases approaching the 4-hour resolution target

---

### FR Category 5: Notification and Customer Dispute

---

#### FR-11 - Real-Time Customer Fraud Notifications

**Stakeholder:** Bank Customer, Compliance Officer

**Requirement:**
The system shall deliver real-time notifications to customers for SOFT_DECLINE and HARD_BLOCK decisions via push notification (Firebase FCM) and/or SMS (Twilio), depending on the customer's registered notification preference. Notifications shall include a non-technical explanation of the action taken and, for HARD_BLOCK, a link to the dispute portal.

**Acceptance Criteria:**
- Notification delivered to customer device within 10 seconds of decision event at P95
- Notification content is human-readable and does not expose technical identifiers, fraud scores, or ML model details
- Notification delivery is confirmed via FCM/Twilio delivery receipt; failed deliveries are retried up to 3 times with exponential backoff
- Customer notification preference (push / SMS / both) is respected in 100% of cases
- Failed notifications after all retries are logged and escalated to the fraud analyst for manual outreach

---

#### FR-12 - Customer Transaction Dispute Submission

**Stakeholder:** Bank Customer, Fraud Analyst

**Requirement:**
The system shall provide an authenticated REST API endpoint allowing customers to submit a formal dispute for any HARD_BLOCK transaction within a configurable dispute window (default: 30 days from the transaction date). Dispute submission shall create a case in the Case Management Service and notify the assigned fraud analyst.

**Acceptance Criteria:**
- Dispute API endpoint (`POST /v1/disputes`) responds within 1 second with a `dispute_id` and estimated resolution timeline
- Dispute records include: `dispute_id`, `transaction_id`, `customer_id_token`, `submitted_at`, `supporting_notes` (text), `status`, `resolved_at`
- Customers cannot submit duplicate disputes for the same transaction (enforced by unique constraint on `transaction_id`)
- Dispute creation triggers a case assignment notification to the fraud analyst queue within 60 seconds
- Dispute resolution (outcome communicated to customer) completed within 48 hours SLA - tracked on the operations dashboard

---

### FR Category 6: MLOps and Model Lifecycle

---

#### FR-13 - Automated Model Retraining Pipeline

**Stakeholder:** ML Engineer, Executive Leadership

**Requirement:**
The system shall support fully automated ML model retraining triggered when the confirmed fraud label buffer accumulates a configurable minimum number of new samples (default: 500). The retraining pipeline shall be orchestrated by Apache Airflow, train new model versions, evaluate them against a held-out validation set, and conditionally promote passing models to production via MLflow.

**Acceptance Criteria:**
- Retraining pipeline triggers automatically within 15 minutes of the label buffer threshold being reached
- Newly trained model achieves precision ≥ 0.85 and recall ≥ 0.80 on the holdout validation set before promotion
- Models failing the evaluation threshold are archived in MLflow with failure reason logged - they are never promoted to production
- End-to-end retraining pipeline (trigger to production promotion) completes within 4 hours for standard retraining runs
- Zero manual steps required for standard retraining cycles - fully hands-off

---

#### FR-14 - Zero-Downtime Model Hot-Swap

**Stakeholder:** ML Engineer, Platform Administrator, Payment Processor Integration Team

**Requirement:**
The system shall support hot-swapping of ML model artifacts in the ML Scoring Service without service restart or scoring downtime. The Model Loader component shall poll the MLflow Model Registry every 60 seconds for new Production-stage model versions and reload them in memory while continuing to serve scoring requests.

**Acceptance Criteria:**
- Hot-swap process completes within 5 seconds of a new Production model version being detected
- Zero scoring requests dropped or delayed beyond the normal P99 latency threshold during a hot-swap event
- Hot-swap events are logged with: `old_model_version`, `new_model_version`, `swap_initiated_at`, `swap_completed_at`, `success` (boolean)
- If a hot-swap fails, the service continues using the previous model version and alerts the ML Engineer via the observability stack within 2 minutes

---

### FR Category 7: Audit, Compliance, and Explainability

---

#### FR-15 - Tamper-Evident Decision Audit Logging

**Stakeholder:** Compliance Officer, Financial Regulator

**Requirement:**
The system shall write a tamper-evident, immutable audit log record for every fraud decision - including APPROVE decisions - synchronously before the decision response is returned. Audit records shall be cryptographically chained to prevent retroactive alteration and retained for a minimum of 7 years.

**Acceptance Criteria:**
- Audit log write is synchronous - decision response is only returned after the audit record is confirmed persisted
- Audit record includes: `decision_id`, `transaction_id`, `account_id_token`, `fraud_score`, `risk_tier`, `decision`, `model_version_composite`, `rule_triggers`, `shap_report_ref`, `decided_at`, `processing_ms`, `record_hash` (SHA-256 of the record content)
- Audit records are stored in append-only PostgreSQL partitioned tables with row-level deletion prevented by database role restrictions
- Any specific audit record is retrievable within 5 seconds by `transaction_id` or `decision_id`
- Data retention: audit records are archived to object storage at 12 months and remain retrievable for 7 years from the decision date

---

## 4. Functional Requirements Traceability Matrix

| Requirement ID | Title | Stakeholder(s) | Priority |
|---|---|---|---|
| FR-01 | Real-Time Transaction Event Ingestion | Payment Processor, Executive Leadership | Must Have |
| FR-02 | Transaction Payload Schema Validation | Payment Processor, Compliance Officer | Must Have |
| FR-03 | PII Tokenisation at Ingestion Boundary | Compliance Officer, Regulator | Must Have |
| FR-04 | ML Ensemble Fraud Scoring | Fraud Analyst, ML Engineer, Executive | Must Have |
| FR-05 | Behavioural Profile-Based Feature Enrichment | Fraud Analyst, ML Engineer | Must Have |
| FR-06 | Configurable Rule-Based Pre-Filters | Platform Admin, Fraud Analyst | Must Have |
| FR-07 | Automated Fraud Decision Enforcement | Customer, Payment Processor, Analyst | Must Have |
| FR-08 | Step-Up Authentication for SOFT_DECLINE | Bank Customer, Compliance Officer | Must Have |
| FR-09 | Automated Fraud Case Generation | Fraud Analyst, Compliance Officer | Must Have |
| FR-10 | Analyst Case Review and Resolution | Fraud Analyst, ML Engineer | Must Have |
| FR-11 | Real-Time Customer Fraud Notifications | Bank Customer, Compliance Officer | Must Have |
| FR-12 | Customer Transaction Dispute Submission | Bank Customer, Fraud Analyst | Should Have |
| FR-13 | Automated Model Retraining Pipeline | ML Engineer, Executive Leadership | Must Have |
| FR-14 | Zero-Downtime Model Hot-Swap | ML Engineer, Platform Admin | Must Have |
| FR-15 | Tamper-Evident Decision Audit Logging | Compliance Officer, Regulator | Must Have |

---

## 4.1 Stakeholder-to-Requirement Traceability Matrix (Two-Way)

The table below provides the reverse mapping - from each stakeholder to every requirement that directly addresses their concerns. This ensures complete bidirectional traceability: every stakeholder concern is covered by at least one requirement, and every requirement can be justified by a stakeholder need.

| Stakeholder | Functional Requirements | Non-Functional Requirements |
|---|---|---|
| **Bank Customer** | FR-07, FR-08, FR-11, FR-12 | NFR-U1, NFR-U3, NFR-P1, NFR-P2, NFR-S2 |
| **Fraud Analyst** | FR-04, FR-05, FR-06, FR-09, FR-10, FR-12 | NFR-U1, NFR-U2, NFR-M1, NFR-P2 |
| **Platform Administrator** | FR-06, FR-14 | NFR-D1, NFR-D2, NFR-D3, NFR-M2, NFR-SC1, NFR-P3 |
| **Compliance Officer** | FR-02, FR-03, FR-06, FR-08, FR-09, FR-11, FR-15 | NFR-U2, NFR-M1, NFR-S1, NFR-S3, NFR-S4 |
| **ML Engineer / Data Scientist** | FR-04, FR-05, FR-13, FR-14 | NFR-D1, NFR-M2, NFR-M3, NFR-SC2 |
| **Payment Processor Integration Team** | FR-01, FR-02, FR-03, FR-07 | NFR-D2, NFR-M1, NFR-P1, NFR-P3 |
| **Financial Regulator (FSCA / SARB)** | FR-03, FR-15 | NFR-S1, NFR-S3, NFR-S4 |
| **Executive Leadership (CTO / CFO)** | FR-01, FR-04, FR-13 | NFR-SC1, NFR-SC2, NFR-P1, NFR-P2, NFR-P3 |

**Coverage verification:**
- Every stakeholder is addressed by at least 3 functional requirements and at least 2 non-functional requirements
- Every requirement (FR-01 through FR-15, NFR-U1 through NFR-P3) maps to at least one stakeholder
- No orphaned requirements exist - full bidirectional traceability confirmed

---

## 5. Non-Functional Requirements

Non-functional requirements define the quality attributes of the system - how well it performs its functions. Requirements are categorised across six quality attribute areas as specified in the assignment rubric.

---

### 5.1 Usability

---

#### NFR-U1 - Fraud Analyst Dashboard Learnability

**Stakeholder:** Fraud Analyst

**Requirement:** The Fraud Analyst Dashboard shall be learnable by a new fraud analyst - with no prior SentinelPay experience - to the level of independently resolving cases without assistance within 2 hours of first use.

**Measurement Criteria:** Usability testing with 5 new analyst participants: average time-to-first-independent-case-resolution ≤ 2 hours. System Usability Scale (SUS) score ≥ 75 (classified as "Good").

---

#### NFR-U2 - SHAP Explanation Readability

**Stakeholder:** Fraud Analyst, Compliance Officer

**Requirement:** SHAP explainability reports displayed in the Analyst Dashboard shall present the top 5 contributing features to the fraud decision in plain English labels - not raw feature variable names - accompanied by a horizontal bar chart showing relative contribution magnitude.

**Measurement Criteria:** In usability testing, ≥ 90% of analyst participants correctly identify the primary fraud signal from a SHAP explanation within 30 seconds without assistance. Zero raw variable names (e.g., `feat_vel_1hr`) displayed in the customer-facing or analyst-facing explanation views - all labels are human-readable (e.g., "Unusually high transaction frequency in the past hour").

---

#### NFR-U3 - Customer Dispute Portal Accessibility

**Stakeholder:** Bank Customer

**Requirement:** The Customer Dispute Portal web interface shall comply with Web Content Accessibility Guidelines (WCAG) 2.1 Level AA accessibility standards to ensure usability for customers with visual, auditory, or motor impairments.

**Measurement Criteria:** Automated accessibility audit using axe-core or equivalent tooling produces zero WCAG 2.1 Level AA violations. Manual screen reader testing (NVDA / VoiceOver) confirms all dispute submission flow steps are fully navigable without a mouse. Colour contrast ratio ≥ 4.5:1 for all body text elements.

---

### 5.2 Deployability

---

#### NFR-D1 - Container-Based Deployment

**Stakeholder:** Platform Administrator, ML Engineer

**Requirement:** Every SentinelPay service shall be packaged as a Docker container image and deployable via Kubernetes manifests on any CNCF-conformant Kubernetes distribution (K3s, EKS, GKE, AKS, or bare-metal kubeadm). A Docker Compose configuration shall additionally be provided for local development and academic demonstration environments.

**Measurement Criteria:** Full system stack deploys successfully from a clean environment using a single `kubectl apply -k .` command within 10 minutes. Docker Compose local stack reaches a healthy state (all service health checks passing) within 5 minutes on a machine with 16GB RAM and 8 CPU cores. Deployment tested and verified on Ubuntu 24.04 LTS and macOS 14+.

---

#### NFR-D2 - Zero-Downtime Production Deployments

**Stakeholder:** Platform Administrator, Payment Processor Integration Team

**Requirement:** All application service deployments shall use Kubernetes rolling update strategy with appropriate readiness probes, ensuring zero dropped requests during a deployment rollout. If a new pod fails its readiness probe, the rollout shall automatically pause and the previous version shall continue serving traffic.

**Measurement Criteria:** Deployment of any service version update results in zero HTTP 5xx errors as measured by the API Gateway during the rollout window. Rollback to the previous version completes within 60 seconds of a failed rollout being detected. Deployment pipeline run (build → push → rolling deploy) completes within 8 minutes end-to-end.

---

#### NFR-D3 - Environment Configuration Externalisation

**Stakeholder:** Platform Administrator

**Requirement:** All environment-specific configuration (database connection strings, Kafka broker addresses, ML model registry URLs, API keys, feature flag values) shall be externalised from container images and injected via Kubernetes ConfigMaps and Secrets. No configuration values shall be hardcoded in application source code or container images.

**Measurement Criteria:** Static analysis scan (e.g., trufflehog, detect-secrets) of the container image layers and source code produces zero hardcoded secrets or environment-specific values. Promoting a deployment from staging to production requires only a Kubernetes namespace/configuration change - no image rebuild required.

---

### 5.3 Maintainability

---

#### NFR-M1 - Comprehensive API Documentation

**Stakeholder:** Payment Processor Integration Team, Compliance Officer, ML Engineer

**Requirement:** All SentinelPay external-facing REST APIs shall be documented using OpenAPI 3.1 specification. API documentation shall be auto-generated from code annotations and served at a live `/docs` endpoint. Documentation shall include request/response schemas, authentication requirements, error codes, and example payloads for every endpoint.

**Measurement Criteria:** OpenAPI specification coverage: 100% of public endpoints documented with request schema, response schema, and at least one example. API documentation rated "complete and accurate" by the Payment Processor Integration Team in integration review. Breaking API changes are versioned - the previous version remains available for a minimum 30-day deprecation window.

---

#### NFR-M2 - Automated Test Coverage

**Stakeholder:** ML Engineer, Platform Administrator

**Requirement:** The SentinelPay codebase shall maintain a minimum test coverage threshold enforced in the CI/CD pipeline. Unit test coverage shall be ≥ 80% for all service modules. Integration tests shall cover all critical inter-service communication paths. The CI pipeline shall fail any pull request that reduces coverage below the threshold.

**Measurement Criteria:** Code coverage report (JaCoCo for Java services, pytest-cov for Python services) shows ≥ 80% line coverage across all modules. CI pipeline build status is "failed" for any PR reducing coverage below threshold - enforced automatically. Integration test suite covers all 8 Kafka topic data flows and all 5 external API integrations.

---

#### NFR-M3 - ML Feature Definition Version Control

**Stakeholder:** ML Engineer

**Requirement:** All ML feature definitions - including feature names, data types, transformation logic, and default values - shall be version-controlled in a shared schema registry accessible by both the Feature Engineering Service (serving) and the MLOps retraining pipeline (training). This eliminates training-serving skew by enforcing a single source of truth for feature definitions.

**Measurement Criteria:** Training-serving skew test: feature vectors generated by the serving pipeline and the training pipeline from identical raw inputs are byte-for-byte identical in 100% of test cases. Feature schema version is included in every model artifact's MLflow metadata. Deploying a new model version with a different feature schema version triggers an automated compatibility check before promotion.

---

### 5.4 Scalability

---

#### NFR-SC1 - Horizontal Auto-Scaling Under Load

**Stakeholder:** Platform Administrator, Executive Leadership

**Requirement:** All SentinelPay microservices shall support horizontal scaling via Kubernetes Horizontal Pod Autoscaler (HPA). The ML Scoring Service and Feature Engineering Service shall automatically scale from a minimum of 2 replicas to a maximum of 20 replicas based on CPU utilisation and custom Kafka consumer lag metrics. Scale-up shall complete within 90 seconds of the trigger threshold being breached.

**Measurement Criteria:** Load test at 3× normal peak (30,000 TPS): HPA scales ML Scoring Service to required replica count within 90 seconds. End-to-end P99 latency remains ≤ 100ms throughout the scale-up event. Scale-down to baseline replica count occurs within 5 minutes of load returning to normal, with no service disruption.

---

#### NFR-SC2 - ML Model Serving Throughput Scalability

**Stakeholder:** ML Engineer, Executive Leadership

**Requirement:** The ML Scoring Service shall be capable of serving ML ensemble inference at a rate of at least 500 scoring requests per second per replica, enabling the system to achieve 10,000 TPS scoring capacity with 20 replicas. Each replica shall be deployable on a standard CPU node (no GPU dependency for inference in production).

**Measurement Criteria:** Single-replica load test: 500 scoring requests/second sustained for 10 minutes with P99 inference latency ≤ 60ms and zero model errors. CPU utilisation per replica under 500 RPS load: ≤ 70% of allocated CPU request. ONNX-exported model variants load and serve correctly on CPU-only nodes without GPU drivers.

---

### 5.5 Security

---

#### NFR-S1 - Encryption in Transit

**Stakeholder:** Compliance Officer, Financial Regulator, Bank Customer

**Requirement:** All network communication between SentinelPay services (inter-service), between services and data stores, and between SentinelPay and external systems shall be encrypted using TLS 1.3. Inter-service communication within the Kubernetes cluster shall additionally use mutual TLS (mTLS) enforced by a service mesh (Istio or Linkerd).

**Measurement Criteria:** Network traffic scan: zero unencrypted inter-service communication detected via Wireshark/tcpdump in the Kubernetes cluster. TLS version audit: zero connections using TLS 1.2 or below accepted by any service endpoint. mTLS enforcement verified: a service without a valid certificate cannot communicate with any other service in the mesh.

---

#### NFR-S2 - Authentication and Authorisation

**Stakeholder:** Compliance Officer, Fraud Analyst, Platform Administrator

**Requirement:** All external-facing REST API endpoints shall be secured using OAuth 2.0 with JWT bearer tokens. Role-based access control (RBAC) shall enforce that: fraud analysts can only access case management and audit report endpoints; platform administrators can access configuration and deployment endpoints; customers can only access their own transaction and dispute data. Token expiry shall be set to a maximum of 1 hour for analyst and admin roles.

**Measurement Criteria:** Penetration test: zero successful unauthorised access to any endpoint using expired, malformed, or cross-role JWT tokens. RBAC enforcement: analyst JWT cannot access admin configuration endpoints (verified by automated security test suite). Customer data isolation: a customer JWT for Account A cannot retrieve data for Account B (enforced by account token binding in JWT claims).

---

#### NFR-S3 - Data Encryption at Rest

**Stakeholder:** Compliance Officer, Financial Regulator

**Requirement:** All data at rest in PostgreSQL, Redis, Cassandra, and MinIO object storage shall be encrypted using AES-256 encryption. Database encryption keys shall be managed by a dedicated key management service (KMS) and rotated on a schedule not exceeding 90 days. Encryption key access shall be restricted to authorised service accounts only.

**Measurement Criteria:** Storage-level encryption verified for all four data stores via provider encryption status API. KMS key rotation executed on schedule: automated rotation job runs every 90 days with rotation confirmed in KMS audit log. Zero service accounts with direct KMS key access beyond those listed in the approved access matrix.

---

#### NFR-S4 - Fraud Decision Audit Log Integrity

**Stakeholder:** Compliance Officer, Financial Regulator

**Requirement:** Audit log records shall be cryptographically signed using HMAC-SHA256 with a KMS-managed signing key to ensure tamper-evidence. Any modification to an audit record shall be detectable by recomputing and comparing the stored `record_hash`. Audit log integrity shall be verified by an automated daily batch process.

**Measurement Criteria:** Tamper detection test: manually modifying any field in an audit record causes the daily integrity check to flag the record as tampered within 24 hours. Integrity verification report produced daily and stored in the compliance officer's report repository. Zero integrity violations detected in production since deployment (tracked as a compliance KPI).

---

### 5.6 Performance

---

#### NFR-P1 - End-to-End Fraud Decision Latency

**Stakeholder:** Payment Processor Integration Team, Bank Customer, Executive Leadership

**Requirement:** The end-to-end fraud decision latency - measured from the moment a transaction event is published to the `transactions.raw` Kafka topic to the moment the decision is published to the `transactions.decisions` Kafka topic - shall not exceed 100 milliseconds at the 99th percentile (P99) under the defined peak load of 10,000 TPS.

**Measurement Criteria:** P50 latency ≤ 40ms; P95 latency ≤ 80ms; P99 latency ≤ 100ms. Measured via OpenTelemetry distributed tracing with trace spans from Kafka consumer offset to Kafka producer acknowledgement. Load test conducted at 10,000 TPS for a minimum 30-minute sustained period. Performance regression: automated pipeline performance test fails if P99 exceeds 100ms in any build.

---

#### NFR-P2 - Analyst Dashboard Response Time

**Stakeholder:** Fraud Analyst, Executive Leadership

**Requirement:** All Fraud Analyst Dashboard API responses shall meet the following response time targets: case queue list endpoint ≤ 2 seconds at P95; individual case detail endpoint (including SHAP chart data) ≤ 3 seconds at P95; case resolution submission endpoint ≤ 1 second at P95. Targets apply under concurrent usage of up to 50 analysts.

**Measurement Criteria:** K6 / JMeter load test simulating 50 concurrent analyst sessions: all three endpoint response time targets met simultaneously. PostgreSQL query execution plan for case queue query uses index scan (not sequential scan) - verified by `EXPLAIN ANALYZE`. Dashboard frontend Lighthouse performance score ≥ 85 for the case list and case detail views.

---

#### NFR-P3 - System Recovery Time Objective

**Stakeholder:** Platform Administrator, Executive Leadership, Payment Processor Integration Team

**Requirement:** In the event of a complete ML Scoring Service failure, the system shall automatically recover to full scoring capacity - using the circuit breaker fallback rule-only scoring mode during recovery - within a Recovery Time Objective (RTO) of 5 minutes. The system shall not lose any transaction events during the outage period due to Kafka's durable message retention.

**Measurement Criteria:** Chaos engineering test (pod deletion of all scoring service replicas): Kubernetes restarts replicas and scoring service passes readiness probe within 3 minutes. Zero transaction events lost during the outage window (verified by Kafka consumer offset comparison before and after recovery). Circuit breaker fallback mode activates within 30 seconds of scoring service failure detection. Full ML ensemble scoring resumes within 5 minutes of pod restart.

---

## 6. Requirements Summary

### Functional Requirements Count

| Category | Requirements | Count |
|---|---|---|
| Transaction Ingestion and Validation | FR-01 to FR-03 | 3 |
| Fraud Scoring and Detection | FR-04 to FR-06 | 3 |
| Decision Engine | FR-07 to FR-08 | 2 |
| Case Management | FR-09 to FR-10 | 2 |
| Notification and Customer Dispute | FR-11 to FR-12 | 2 |
| MLOps and Model Lifecycle | FR-13 to FR-14 | 2 |
| Audit, Compliance, and Explainability | FR-15 | 1 |
| **Total** | | **15** |

### Non-Functional Requirements Count

| Category | Requirements | Count |
|---|---|---|
| Usability | NFR-U1 to NFR-U3 | 3 |
| Deployability | NFR-D1 to NFR-D3 | 3 |
| Maintainability | NFR-M1 to NFR-M3 | 3 |
| Scalability | NFR-SC1 to NFR-SC2 | 2 |
| Security | NFR-S1 to NFR-S4 | 4 |
| Performance | NFR-P1 to NFR-P3 | 3 |
| **Total** | | **18** |

---

## 7. Glossary

| Term | Definition |
|---|---|
| **AES-256** | Advanced Encryption Standard with 256-bit key length - a symmetric encryption algorithm used for data at rest |
| **CSAT** | Customer Satisfaction Score - a survey-based metric measuring customer satisfaction on a numerical scale |
| **FSCA** | Financial Sector Conduct Authority - South Africa's financial services market conduct regulator |
| **HPA** | Horizontal Pod Autoscaler - a Kubernetes controller that automatically scales pod replicas based on observed metrics |
| **mTLS** | Mutual TLS - a variant of TLS where both client and server authenticate each other using certificates |
| **POPIA** | Protection of Personal Information Act - South Africa's primary data protection legislation |
| **P99** | 99th percentile latency - the latency below which 99% of requests are served |
| **RBAC** | Role-Based Access Control - a security model where access rights are assigned based on user roles |
| **RTO** | Recovery Time Objective - the maximum acceptable time to restore service after a failure |
| **SARB** | South African Reserve Bank - South Africa's central bank and prudential financial regulator |
| **SHAP** | SHapley Additive exPlanations - a method for explaining the output of ML models using game-theoretic principles |
| **SRD** | System Requirements Document - this document |
| **TPS** | Transactions Per Second - a throughput measurement for transaction processing systems |
| **WCAG** | Web Content Accessibility Guidelines - internationally recognised web accessibility standards published by W3C |

---

*SentinelPay SRD.md - Version 2.0 | March 2026*
*Assignment 4 - System Requirements Documentation | Builds on Assignment 3*