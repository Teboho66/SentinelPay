# USE_CASE_SPECIFICATIONS.md - Use Case Specifications
## SentinelPay: Real-Time Fraud Detection & Prevention Engine

> **Assignment 5 - Use Case Specifications**
> 8 critical use cases selected from the Use Case Diagram in USE_CASE_DIAGRAM.md
> All use cases trace directly to functional requirements in SRD.md

---

## Selection Rationale

The following 8 use cases were selected as critical because they cover the core system pipeline end-to-end - from transaction submission through scoring, decision enforcement, customer response, analyst investigation, audit, and model improvement. Together they represent the complete fraud detection lifecycle and touch every stakeholder identified in STAKEHOLDER_ANALYSIS.md.

| # | Use Case | Requirement(s) | Stakeholder(s) |
|---|---|---|---|
| UC1 | Submit Transaction | FR-01, FR-02 | Payment Processor |
| UC3 | Score Transaction for Fraud | FR-04, FR-05 | Fraud Analyst, ML Engineer |
| UC4 | Enforce Fraud Decision | FR-07, FR-08 | Bank Customer, Payment Processor |
| UC5 | Complete Step-Up Authentication | FR-08 | Bank Customer |
| UC7 | Submit Transaction Dispute | FR-12 | Bank Customer |
| UC8 | Review and Resolve Fraud Case | FR-09, FR-10 | Fraud Analyst |
| UC10 | Retrain Fraud Detection Model | FR-13, FR-14 | ML Engineer |
| UC11 | Generate Audit Report | FR-15 | Compliance Officer, Regulator |

---

## UC1 - Submit Transaction

**Actor:** Payment Processor (System Actor)
**Related Requirements:** FR-01, FR-02, FR-03
**Stakeholders:** Payment Processor Integration Team, Compliance Officer

### Description
The Payment Processor submits a financial transaction event to SentinelPay for real-time fraud evaluation. This is the entry point into the entire SentinelPay pipeline. Every subsequent use case in the system depends on a successfully submitted and validated transaction. The use case covers the full ingestion cycle - schema validation, PII tokenisation, and routing to the scoring pipeline.

### Preconditions
- The Payment Processor system has an active, authenticated Kafka producer connection to SentinelPay's `transactions.raw` topic
- The transaction event is formatted as a JSON payload
- The SentinelPay Transaction Ingestion Service is running and consuming from the `transactions.raw` topic
- The PII token vault service is available

### Postconditions
- **Success:** A validated, PII-tokenised transaction event is published to the `transactions.enriched` Kafka topic, ready for feature engineering and ML scoring
- **Failure:** A structured error payload is published to the `transactions.dlq` dead-letter queue with the specific validation failure reason, and an error log entry is written to the observability stack

### Basic Flow
1. Payment Processor publishes a transaction JSON payload to the `transactions.raw` Kafka topic
2. Transaction Ingestion Service consumes the event within 5ms of publication
3. System validates the payload against the active JSON schema version, checking all mandatory fields: `transaction_id`, `account_id`, `merchant_id`, `merchant_category_code`, `amount`, `currency`, `timestamp`, `channel`, `device_fingerprint_token`, `ip_address_hash`, `geolocation`
4. System tokenises PII fields - `account_id` becomes `acc_token_xxxx`, `device_fingerprint` becomes `dfp_token_xxxx`, `ip_address` is hashed - via the token vault service
5. System enriches the event with the current threat intelligence signals (known bad IPs, compromised card BINs) fetched from the threat intelligence feed cache
6. System publishes the validated, tokenised, enriched event to the `transactions.enriched` Kafka topic with the active schema version number included in the payload header
7. Feature Engineering Service picks up the enriched event to begin UC3

### Alternative Flows

**AF-01: Missing mandatory field**
- At step 3, the system detects one or more mandatory fields are absent from the payload
- System immediately routes the event to `transactions.dlq` with error code `SCHEMA_VALIDATION_FAILED` and a list of the specific missing fields
- System writes a structured error log entry including `transaction_id` (if present), `error_code`, `missing_fields`, and `timestamp`
- The Payment Processor is not notified synchronously - the dead-letter queue is monitored by the Platform Administrator
- Basic flow ends

**AF-02: Invalid field type or format**
- At step 3, a mandatory field is present but fails type validation (e.g., `amount` is a string instead of a decimal, `timestamp` is not ISO 8601)
- System routes to `transactions.dlq` with error code `SCHEMA_TYPE_ERROR` and the specific field name and received value
- Basic flow ends

**AF-03: PII token vault unavailable**
- At step 4, the token vault service returns a timeout or connection error
- System does not proceed with an untokenised event
- System routes the event to `transactions.dlq` with error code `TOKENISATION_FAILED`
- System triggers an alert to the Platform Administrator via the observability stack
- Basic flow ends

**AF-04: Duplicate transaction ID**
- At step 6, the system detects the `transaction_id` already exists in the deduplication cache (Redis, 24-hour TTL)
- System discards the duplicate event and writes a `DUPLICATE_TRANSACTION` log entry
- Basic flow ends

---

## UC3 - Score Transaction for Fraud

**Actor:** ML Engineer (indirect - owns the models), Payment Processor (initiates via UC1)
**Related Requirements:** FR-04, FR-05, FR-06
**Stakeholders:** Fraud Analyst, ML Engineer, Executive Leadership

### Description
SentinelPay scores every validated transaction using a three-model ML ensemble: XGBoost gradient boosting, Isolation Forest anomaly detection, and a fine-tuned DistilBERT merchant text classifier. The ensemble produces a composite `fraud_score` between 0.0 and 1.0 and a `risk_tier` of LOW, MEDIUM, HIGH, or CRITICAL. This is the core intelligence of SentinelPay and must complete within 60ms to meet the overall 100ms pipeline SLA.

### Preconditions
- A validated, tokenised transaction event is available on the `transactions.features` Kafka topic
- All three ML model versions (XGBoost, Isolation Forest, DistilBERT) are loaded in memory by the Model Loader component
- The account's behavioural profile is available in Redis (or Cassandra for new accounts)
- The circuit breaker is in CLOSED state (normal operation)

### Postconditions
- **Success:** A scored result payload is published to the `transactions.scored` Kafka topic, containing: `fraud_score`, `risk_tier`, `model_version_composite`, `component_scores` (one per sub-model), `shap_report_ref` (if applicable), and `processing_ms`
- **Failure (circuit breaker open):** A fallback rule-only score is published with `fallback_mode_active: true` and an alert is raised to the ML Engineer

### Basic Flow
1. Feature Engineering Service consumes the enriched event from `transactions.enriched`
2. System queries Redis for the account's real-time behavioural profile (velocity counters, avg amount, known devices)
3. System builds the ML feature vector: amount deviation from 30-day baseline, velocity in past 1hr/6hr/24hr, geo-velocity score, device novelty flag, merchant risk score, hour-of-day, is_international flag
4. Feature vector is validated against the active Pydantic schema to prevent training-serving skew
5. ML Scoring Service runs all three sub-models in parallel:
   - XGBoost classifies the tabular feature vector and returns a fraud probability (0.0-1.0)
   - Isolation Forest evaluates structural anomaly and returns a normalised anomaly score
   - DistilBERT classifies merchant name and MCC text and returns a merchant risk score
6. Ensemble Aggregator combines the three scores using calibrated weights (XGBoost 60%, Isolation Forest 25%, DistilBERT 15%) to produce a composite `fraud_score`
7. `fraud_score` is mapped to a `risk_tier` using the configured threshold table
8. For scores above the SOFT_DECLINE threshold, SHAP explainability computation is queued as an async background job
9. Scored result is published to `transactions.scored` Kafka topic
10. Redis velocity counters for the account are atomically incremented

### Alternative Flows

**AF-01: Single sub-model inference failure**
- At step 5, one of the three sub-models throws an exception or times out
- Circuit breaker records the failure
- Ensemble Aggregator re-weights the remaining two models proportionally and produces a degraded-mode score
- Scored result includes `degraded_mode: true` and identifies the failed model
- Alert raised to ML Engineer via Prometheus/Grafana
- Basic flow continues with degraded score

**AF-02: All sub-models fail or circuit breaker open**
- At step 5, all models fail or the circuit breaker is already OPEN from a previous failure window
- System activates rule-only fallback scoring using pre-filter rules (velocity, blacklist, amount limits)
- Fallback score published with `fallback_mode_active: true`
- Alert raised immediately to ML Engineer and Platform Administrator
- Basic flow ends with fallback result

**AF-03: New account with insufficient history**
- At step 2, the account has fewer than 10 historical transactions
- System uses population-average behavioural baselines instead of account-specific ones
- A configurable new-account risk boost is added to the final `fraud_score`
- `new_account_flag: true` is included in the scored result

**AF-04: Feature vector schema mismatch**
- At step 4, the feature vector fails Pydantic schema validation due to a missing or malformed feature
- Event is routed to `transactions.dlq` with error code `FEATURE_SCHEMA_MISMATCH`
- Alert raised to ML Engineer indicating potential training-serving skew

---

## UC4 - Enforce Fraud Decision

**Actor:** Payment Processor (receives decision), Bank Customer (affected)
**Related Requirements:** FR-07, FR-08, FR-11
**Stakeholders:** Bank Customer, Payment Processor Integration Team, Fraud Analyst

### Description
The Decision Engine consumes the scored transaction from UC3 and applies configurable business rules and per-account-tier thresholds to produce a final decision: APPROVE, SOFT_DECLINE, or HARD_BLOCK. This decision is the output that the Payment Processor acts on. APPROVE transactions are cleared. SOFT_DECLINE triggers step-up authentication (UC5). HARD_BLOCK triggers immediate notification to the customer (UC6) and case generation (UC9).

### Preconditions
- A scored transaction result is available on the `transactions.scored` Kafka topic
- Decision threshold configuration is loaded for the relevant account tier (Standard, Premium, Business)
- Notification Orchestrator is available to receive decision events

### Postconditions
- **APPROVE:** Decision record persisted in PostgreSQL. Decision published to `transactions.decisions` topic. Payment Processor receives APPROVE response.
- **SOFT_DECLINE:** Decision record persisted. Step-up authentication challenge triggered (UC5). Payment Processor receives provisional HOLD response.
- **HARD_BLOCK:** Decision record persisted. Customer fraud notification triggered. Fraud case auto-generated if risk_tier is HIGH or CRITICAL. Payment Processor receives BLOCK response.

### Basic Flow
1. Decision Engine consumes scored transaction from `transactions.scored` Kafka topic
2. System retrieves the account tier (Standard / Premium / Business) for the transacting account
3. System applies the pre-filter rule check results - if a pre-filter blacklist match exists, skip to step 6 with HARD_BLOCK
4. System evaluates the `fraud_score` against the threshold table for the account tier:
   - Score < LOW threshold: decision = APPROVE
   - LOW threshold <= score < HIGH threshold: decision = SOFT_DECLINE
   - Score >= HIGH threshold: decision = HARD_BLOCK
5. System writes the decision record to PostgreSQL with all required fields including `rule_triggers` array and `processing_ms`
6. System publishes the decision event to `transactions.decisions` Kafka topic
7. Notification Orchestrator consumes the event and dispatches notification to customer for SOFT_DECLINE and HARD_BLOCK (UC6)
8. For HARD_BLOCK with risk_tier HIGH or CRITICAL, Case Management Service auto-generates a fraud investigation case (UC9)
9. Audit Service writes a tamper-evident audit log record for every decision including APPROVE

### Alternative Flows

**AF-01: Threshold configuration not found for account tier**
- At step 2, no threshold configuration exists for the account's tier
- System applies the default Standard tier thresholds as a safe fallback
- Decision log includes `threshold_fallback: true` flag
- Alert raised to Platform Administrator

**AF-02: Decision Engine downstream write failure**
- At step 5, PostgreSQL write fails
- System retries the write up to 3 times with exponential backoff
- If all retries fail, system does not publish the decision and raises a P1 alert to Platform Administrator
- Transaction is held pending manual resolution

**AF-03: Score falls exactly on threshold boundary**
- At step 4, `fraud_score` equals exactly the configured threshold value
- System applies the rule: boundary scores are treated as meeting the higher-risk tier (e.g., score exactly equal to HIGH threshold = HARD_BLOCK)
- This boundary rule is documented in the threshold configuration

---

## UC5 - Complete Step-Up Authentication

**Actor:** Bank Customer
**Related Requirements:** FR-08
**Stakeholders:** Bank Customer, Compliance Officer

### Description
When a transaction receives a SOFT_DECLINE decision, the Bank Customer is given the opportunity to prove their identity through a step-up authentication challenge rather than having their transaction immediately hard-blocked. They receive a one-time passcode (OTP) via SMS or push notification and must submit it within a configurable timeout window (default 120 seconds). Success results in the transaction being approved. Timeout or failure results in escalation to HARD_BLOCK.

### Preconditions
- A SOFT_DECLINE decision has been made for the customer's transaction (UC4 completed)
- The customer has a registered mobile number or push notification token on file
- The Notification Gateway (Twilio / Firebase FCM) is available
- The step-up challenge is still within the timeout window

### Postconditions
- **Success:** Transaction decision updated to APPROVE. Customer notified of successful authentication. Decision audit record updated with `step_up_outcome: SUCCESS`.
- **Timeout:** Decision escalated to HARD_BLOCK. Customer notified that the transaction was blocked. Fraud case generated if risk_tier is HIGH or CRITICAL.
- **Failure (wrong OTP):** Decision escalated to HARD_BLOCK after maximum attempts (default: 3). Fraud case generated.

### Basic Flow
1. Notification Orchestrator receives the SOFT_DECLINE event from the decisions topic
2. System generates a cryptographically secure 6-digit OTP with a 120-second expiry
3. OTP is stored in Redis with the `transaction_id` as the key and 120-second TTL
4. System dispatches an OTP notification to the customer via their preferred channel (push notification or SMS) within 5 seconds
5. Customer receives the notification and enters the OTP in their banking app or web portal
6. Customer submits the OTP via the `POST /v1/auth/step-up` API endpoint
7. System validates the OTP against the Redis-stored value - checks match and expiry
8. System updates the transaction decision to APPROVE in PostgreSQL
9. System publishes an APPROVE decision event to `transactions.decisions` topic
10. Customer receives a confirmation notification that the transaction was approved

### Alternative Flows

**AF-01: OTP timeout (120 seconds elapsed)**
- At step 7, the Redis key has expired (TTL reached)
- System treats the submission as invalid
- Decision escalated to HARD_BLOCK
- Customer receives a notification: "Your verification window has expired. The transaction has been blocked for your security."
- Fraud case generated via UC9 if risk_tier is HIGH or CRITICAL

**AF-02: Wrong OTP submitted**
- At step 7, the submitted OTP does not match the stored value
- System increments the attempt counter for this `transaction_id` in Redis
- If attempts < 3: Customer receives "Incorrect code. X attempts remaining." and may retry
- If attempts >= 3: Decision escalated to HARD_BLOCK. All subsequent OTP submissions for this transaction are rejected.

**AF-03: Notification delivery failure**
- At step 4, the Notification Gateway returns a delivery failure after 3 retry attempts
- System logs a `NOTIFICATION_DELIVERY_FAILED` event
- System attempts to deliver via the secondary notification channel (e.g., SMS if push failed)
- If both channels fail: Decision automatically escalated to HARD_BLOCK to prevent indefinite transaction hold. Alert raised to Platform Administrator.

**AF-04: Customer resend OTP request**
- Customer requests a new OTP before the original expires
- System invalidates the previous OTP in Redis and generates a new one
- New OTP dispatched with a fresh 120-second window
- Resend is rate-limited to 3 requests per transaction

---

## UC7 - Submit Transaction Dispute

**Actor:** Bank Customer
**Related Requirements:** FR-12
**Stakeholders:** Bank Customer, Fraud Analyst

### Description
A Bank Customer whose transaction was HARD_BLOCKED may formally dispute the decision through the Customer Dispute Portal within 30 days of the transaction date. The dispute submission creates a priority case in the Case Management Service and notifies the fraud analyst queue. The customer receives a dispute reference number and an estimated resolution timeline. This use case is critical for maintaining customer trust when false positives occur.

### Preconditions
- The customer is authenticated in the Customer Dispute Portal (valid OAuth2 / JWT session)
- The transaction being disputed has a HARD_BLOCK decision in the system
- The transaction date is within the configurable dispute window (default: 30 days)
- No existing dispute has already been submitted for this transaction

### Postconditions
- **Success:** A dispute record is created in PostgreSQL with a unique `dispute_id`. A case is created or updated in the Case Management Service. The assigned fraud analyst receives a queue notification. Customer receives a confirmation with `dispute_id` and 48-hour resolution SLA.
- **Failure:** Customer receives an appropriate error message. No duplicate dispute is created.

### Basic Flow
1. Customer navigates to the HARD_BLOCKED transaction in the Customer Dispute Portal
2. Customer selects "Dispute this transaction" and is presented with the dispute form
3. Customer optionally enters a supporting note explaining why the transaction was legitimate
4. Customer submits the dispute via `POST /v1/disputes`
5. System validates: transaction exists, was HARD_BLOCKED, is within the 30-day dispute window, no prior dispute exists for this `transaction_id`
6. System creates a dispute record in PostgreSQL with status `OPEN`
7. System creates or links a fraud investigation case in the Case Management Service with priority derived from the original `fraud_score`
8. System publishes a dispute notification event to the fraud analyst queue
9. System returns HTTP 201 with `dispute_id` and estimated resolution time (48 hours from submission)
10. Customer receives a confirmation notification via their preferred channel

### Alternative Flows

**AF-01: Transaction not found or not HARD_BLOCKED**
- At step 5, the `transaction_id` does not exist or the decision was not HARD_BLOCK
- System returns HTTP 404 with message: "Transaction not found or is not eligible for dispute."
- No dispute record created

**AF-02: Dispute window expired**
- At step 5, the transaction date is more than 30 days ago
- System returns HTTP 422 with message: "The dispute window for this transaction has closed. Please contact your bank directly."
- No dispute record created

**AF-03: Duplicate dispute submission**
- At step 5, a dispute already exists for this `transaction_id`
- System returns HTTP 409 with the existing `dispute_id` and its current status
- No new dispute record created

**AF-04: Dispute portal session expired during submission**
- At step 4, the customer's JWT token has expired
- System returns HTTP 401
- Customer is redirected to re-authenticate
- Dispute form data is preserved in session storage where possible

---

## UC8 - Review and Resolve Fraud Case

**Actor:** Fraud Analyst
**Related Requirements:** FR-09, FR-10, FR-13
**Stakeholders:** Fraud Analyst, ML Engineer, Compliance Officer

### Description
The Fraud Analyst reviews cases in their queue, investigates the transaction details, account behavioural history, and SHAP explainability report, then makes a resolution decision: CONFIRMED_FRAUD or FALSE_POSITIVE. This is one of the most consequential use cases in the system because the resolution feeds directly into the ML retraining pipeline. A high-quality analyst decision improves future model accuracy. This use case includes UC14 (View SHAP Explainability Report) as a mandatory sub-step.

### Preconditions
- The analyst is authenticated in the Fraud Analyst Dashboard (valid OAuth2 session with analyst RBAC role)
- At least one case exists in the analyst's queue with status OPEN or IN_REVIEW
- The case's associated transaction record exists in PostgreSQL
- The SHAP explainability report has been generated (async job from UC3 has completed)

### Postconditions
- **CONFIRMED_FRAUD:** Case status updated to CONFIRMED. A labelled fraud sample is published to the MLOps retraining buffer. Customer is notified their disputed transaction (if applicable) has been confirmed as fraud. Account risk profile is updated.
- **FALSE_POSITIVE:** Case status updated to DISMISSED. If the case originated from a customer dispute (UC7), the dispute is resolved in the customer's favour and they are notified. Model false positive signal is recorded for analyst reporting.

### Basic Flow
1. Analyst opens the Fraud Analyst Dashboard and views their prioritised case queue (P1 cases first)
2. Analyst selects a case to review - dashboard loads within 2 seconds
3. System displays the case detail view including: transaction details, account behavioural summary (velocity history, known devices, typical locations), fraud score, risk tier, and rule triggers
4. System displays the SHAP explainability report (UC14) - top 5 contributing features shown as a bar chart with human-readable labels
5. Analyst reviews all evidence and optionally cross-references the account's full transaction history
6. Analyst selects resolution: CONFIRMED_FRAUD or FALSE_POSITIVE
7. Analyst optionally enters an investigation note (required for FALSE_POSITIVE resolutions to capture reasoning)
8. Analyst submits the resolution via the dashboard
9. System persists the resolution to PostgreSQL within 1 second, updating `case_status`, `resolved_at`, `analyst_id`, and `note`
10. If CONFIRMED_FRAUD: system publishes a labelled fraud sample (`transaction_id`, `features`, `label: fraud`) to the Kafka `fraud.labels` topic within 60 seconds, feeding UC10
11. System updates the analyst's SLA tracker - removes the case from the pending queue

### Alternative Flows

**AF-01: SHAP report not yet generated**
- At step 4, the async SHAP job is still in progress
- Dashboard displays a "Generating explanation... please wait" indicator
- System polls for SHAP completion every 3 seconds
- If SHAP is not available after 5 minutes, dashboard displays: "Explanation unavailable for this case. Proceed with manual investigation."
- Analyst may still resolve the case - resolution is not blocked by SHAP availability

**AF-02: Analyst reassigns case**
- At step 6, the analyst determines the case requires senior review
- Analyst selects "Reassign" and selects a senior analyst from the available list
- Case status updated to IN_REVIEW with new `assigned_analyst_id`
- New analyst receives a queue notification

**AF-03: Resolution submission failure**
- At step 9, the PostgreSQL write fails
- System displays an error notification and retries automatically
- Analyst's resolution input is preserved in the dashboard - no data loss
- If retry fails, case remains OPEN and the analyst is instructed to try again

**AF-04: SLA breach warning**
- During review, if the case has been OPEN for more than 3 hours 45 minutes (approaching the 4-hour SLA)
- Dashboard displays a red SLA warning badge on the case
- System sends a notification to the analyst's manager if the case reaches 4 hours without resolution

---

## UC10 - Retrain Fraud Detection Model

**Actor:** ML Engineer
**Related Requirements:** FR-13, FR-14
**Stakeholders:** ML Engineer, Executive Leadership

### Description
The MLOps retraining pipeline automatically retrains the fraud detection ensemble when the confirmed fraud label buffer reaches the configured threshold (default: 500 new confirmed fraud samples). This use case is initiated by an Apache Airflow DAG scheduler but is owned and monitored by the ML Engineer. The retrained model is evaluated on a holdout validation set before promotion to production. This use case includes UC3 (Score Transaction for Fraud) as a mandatory sub-step for holdout set evaluation.

### Preconditions
- The confirmed fraud label buffer in the MLOps pipeline has reached the configured threshold (default: 500 samples)
- The Apache Airflow scheduler is running and the retraining DAG is enabled
- Historical feature data is available in Apache Cassandra
- The MLflow Model Registry is accessible
- The current production model version is stable (not in a degraded or fallback state)

### Postconditions
- **Success (model promoted):** New model version tagged as Production in MLflow. Old model version tagged as Archived. ML Scoring Service hot-swaps to new model within 60 seconds via UC14. MLflow experiment logged with all metrics.
- **Failure (model rejected):** New model version tagged as Failed in MLflow with failure reason. Current production model remains unchanged. ML Engineer notified via alert.

### Basic Flow
1. Airflow DAG triggers when the `fraud.labels` Kafka topic consumer group lag indicates 500+ unconsumed labels
2. Pipeline fetches all new confirmed fraud labels from the labels buffer along with their feature vectors from Cassandra
3. Pipeline combines new labels with existing training data and splits into training set (80%) and holdout validation set (20%)
4. Pipeline trains new XGBoost, Isolation Forest, and DistilBERT model versions in parallel using the updated training set
5. Pipeline evaluates the new ensemble on the holdout validation set using UC3 (scoring inference) to confirm inference pipeline compatibility
6. Pipeline computes precision, recall, F1-score, and AUC-ROC for the new ensemble on the holdout set
7. Pipeline compares metrics against the promotion gate: precision >= 0.85 AND recall >= 0.80
8. If gate passed: new model versions are registered in MLflow as Staging, then promoted to Production after a 5-minute monitoring window
9. ML Scoring Service Model Loader detects the new Production version within 60 seconds and hot-swaps without service restart (FR-14)
10. Airflow DAG logs the experiment run in MLflow with all training parameters, metrics, and artifact references

### Alternative Flows

**AF-01: Model fails precision/recall gate**
- At step 7, the new model does not meet the promotion threshold
- Pipeline tags the new model version as Failed in MLflow with the specific metrics that failed
- Current production model remains active
- ML Engineer receives an alert with the full evaluation report
- Pipeline suggests root cause analysis: insufficient new training data, data drift, or feature engineering issue

**AF-02: Training data volume insufficient**
- At step 3, the combined dataset has fewer than 1,000 samples (insufficient for reliable retraining)
- Airflow DAG pauses the retraining run and logs a warning
- ML Engineer is notified: "Insufficient training data - retraining deferred until label buffer grows"
- DAG reschedules for the next trigger threshold

**AF-03: MLflow registry unavailable**
- At step 8, MLflow is unreachable when attempting to register the new model
- Pipeline retries the registration 3 times with exponential backoff
- If all retries fail, new model artifact is saved locally as a failsafe
- ML Engineer receives a critical alert - manual MLflow registration required
- Existing production model continues to serve

**AF-04: Hot-swap failure after promotion**
- At step 9, the ML Scoring Service fails to load the new model version
- Model Loader reverts to the previous production model version automatically
- MLflow model stage is rolled back to the previous Production version
- ML Engineer receives an alert with the hot-swap error log

---

## UC11 - Generate Audit Report

**Actor:** Compliance Officer, Financial Regulator
**Related Requirements:** FR-15
**Stakeholders:** Compliance Officer, Financial Regulator (FSCA / SARB)

### Description
The Compliance Officer or Financial Regulator requests a formal audit report covering fraud decisions made within a specified date range. The report can be scoped to all decisions, specific decision types (HARD_BLOCK only), or a specific transaction. Every report is generated from the tamper-evident audit log, with cryptographic integrity verification performed before the report is compiled. This use case is the primary mechanism through which SentinelPay satisfies its regulatory examination obligations.

### Preconditions
- The requesting actor is authenticated with the Compliance Officer or Regulator RBAC role
- The Audit Service is running and the PostgreSQL audit log is accessible
- The requested date range falls within the 7-year retention window
- The MinIO object store is accessible (for retrieving SHAP report references)

### Postconditions
- **Success:** A structured audit report is generated and delivered to the requester as a downloadable JSON or PDF document. Every decision in the report has been integrity-verified. The report generation event is itself logged in the audit trail.
- **Failure:** Requester receives an appropriate error. No partial report is delivered.

### Basic Flow
1. Compliance Officer accesses the Audit Report portal in the Admin interface
2. Compliance Officer specifies report parameters: date range, decision type filter (ALL / SOFT_DECLINE / HARD_BLOCK), and optionally a specific `transaction_id`
3. Compliance Officer submits the report request via `POST /v1/audit/reports`
4. Audit Service retrieves all matching audit records from PostgreSQL within the specified parameters
5. System performs cryptographic integrity verification on each retrieved record: recomputes `record_hash` using HMAC-SHA256 and compares to stored value
6. If any record fails integrity verification, system flags it in the report with `integrity_status: TAMPERED` and raises an immediate alert to the Compliance Officer
7. System resolves `shap_report_ref` references - fetches SHAP report documents from MinIO object store for HARD_BLOCK decisions
8. System compiles the full report with: report metadata, integrity verification summary, decision records with all audit fields, and SHAP report references
9. System generates the report as a downloadable PDF and JSON
10. Report is delivered to the requester and the report generation event is logged in the audit trail

### Alternative Flows

**AF-01: Integrity verification failure detected**
- At step 6, one or more audit records fail the HMAC-SHA256 integrity check
- System flags all affected records with `integrity_status: TAMPERED` and includes them in the report with a prominent warning
- System immediately raises a P0 security alert to the Compliance Officer and Platform Administrator
- Report is still delivered with the tamper flags visible - a partial report is not suppressed
- Compliance Officer must initiate a formal incident investigation

**AF-02: Date range exceeds available retention window**
- At step 4, part of the requested date range falls outside the 7-year retention window
- System returns available records within the valid window and includes a notice: "Records prior to [date] are outside the retention window and are not available."
- Report is generated for the available date range only

**AF-03: Single transaction not found**
- At step 4, a specific `transaction_id` is requested but does not exist in the audit log
- System returns HTTP 404 with message: "No audit record found for this transaction ID."
- No report generated

**AF-04: Large report generation timeout**
- At step 8, the report covers a very large date range resulting in hundreds of thousands of records
- System switches to asynchronous report generation and returns HTTP 202 Accepted with a `report_job_id`
- System notifies the requester via email/notification when the report is ready for download (estimated time included in the 202 response)

---

*SentinelPay USE_CASE_SPECIFICATIONS.md - Version 1.0 | March 2026*
*Assignment 5 - Builds on Assignments 3 and 4*