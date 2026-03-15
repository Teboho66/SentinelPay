# SPECIFICATION.md - SentinelPay: Real-Time Fraud Detection & Prevention Engine

---

## 1. Introduction

### 1.1 Project Title
**SentinelPay - Real-Time Fraud Detection & Prevention Engine**

### 1.2 Domain

**Domain:** FinTech - Digital Payments & Financial Crime Prevention

The FinTech domain encompasses the intersection of financial services and technology, specifically the infrastructure that enables digital payments, mobile banking, credit transactions, and real-time fund transfers. Within this domain, **financial crime prevention** is a regulatory-mandated and business-critical function. Every licensed payment service provider, bank, and digital wallet operator is legally obligated to maintain Anti-Money Laundering (AML) and fraud prevention mechanisms that are auditable and effective.

In 2026, the digital payments landscape is characterised by:
- **Instant payment rails** (e.g., South Africa's RTC/PayShap, EU's SEPA Instant, US FedNow) where irrevocable transactions settle in under 10 seconds
- **AI-generated synthetic identity fraud** -
 where machine-learning tools are used by fraudsters to generate convincing fake identity documents, creating new fraud vectors
- **Cross-border transaction complexity** - real-time multi-currency flows that span regulatory jurisdictions
- **Open Banking APIs** exposing financial data to third-party providers, increasing the attack surface

The consequence of inadequate fraud detection in this domain is direct, measurable financial loss - to consumers, to institutions, and to systemic trust in digital finance. According to industry data, global payment fraud losses exceeded **$48 billion USD in 2025**, with card-not-present (CNP) fraud being the dominant vector.

### 1.3 Problem Statement

Financial institutions and FinTech platforms process millions of transactions per day. Traditional rule-based fraud detection systems - built on static thresholds and hand-crafted decision trees - are no longer sufficient against the adaptive, AI-assisted fraud techniques of 2026.

**Core problems being solved:**

1. **Latency Gap:** Legacy fraud systems operate in batch or near-real-time mode (5–30 second decision cycles). Modern instant payment rails require fraud decisions in **under 100 milliseconds**, before the transaction settles.

2. **Model Staleness:** Static rule sets cannot adapt to emerging fraud patterns. Without a feedback loop, detection rates degrade over time as fraudsters adapt.

3. **False Positive Cost:** Overly aggressive fraud rules block legitimate transactions, directly harming customer experience and revenue. In 2025, false positives cost the global payments industry an estimated R443 billion in declined legitimate sales.

4. **Explainability Deficit:** Regulators (under POPIA, PSD2, GDPR, and Basel III frameworks) now require that automated financial decisions be explainable and auditable. Black-box models alone are insufficient.

5. **Siloed Detection:** Fraud signals across channels (card payments, mobile transfers, account logins, merchant onboarding) are not correlated, allowing multi-channel fraud attacks to evade channel-specific detectors.

**SentinelPay solves these problems** through a unified, event-driven fraud intelligence platform that operates in true real-time, learns continuously, and produces explainable, auditable decisions.

### 1.4 Individual Scope & Feasibility Justification

SentinelPay is scoped as a **fully-specified software system** designed for individual academic delivery. The following justifies its feasibility within a single-semester postgraduate project:

| Concern | Justification |
|---|---|
| **Technical Complexity** | Core detection pipeline (Kafka → scoring service → decision engine) is implementable in Java/Python using well-documented open-source frameworks |
| **ML Component** | Pre-trained anomaly detection models (Isolation Forest, XGBoost) are available via scikit-learn and can be trained on synthetic transaction datasets (e.g., IEEE-CIS Fraud Detection dataset on Kaggle) |
| **Infrastructure** | Docker Compose enables full local deployment of all services without cloud spend |
| **Data** | IEEE-CIS Fraud Detection dataset (590k transactions) and PaySim synthetic mobile money dataset provide realistic training and testing data |
| **Regulatory Layer** | Explainability via SHAP is a well-understood, implementable Python library - full regulatory simulation is out of scope but the architecture accommodates it |
| **Boundaries (Out of Scope)** | Production cloud deployment, real bank API integrations, licensed payment network access |

The system is ambitious but tractable - it maps directly to skills covered in the programme (system design, distributed systems, ML integration, API design) and produces meaningful academic output at all specification and architecture levels.

---

## 2. Functional Requirements

### 2.1 Transaction Ingestion
- **FR-01:** The system shall ingest transaction events from external payment sources via a Kafka topic (`transactions.raw`) in real time
- **FR-02:** The system shall support transaction payloads conforming to a defined JSON schema including: `transaction_id`, `account_id`, `merchant_id`, `amount`, `currency`, `timestamp`, `channel`, `device_fingerprint`, `geolocation`, `ip_address`
- **FR-03:** The system shall validate all incoming transaction payloads and route malformed events to a dead-letter queue (`transactions.dlq`)

### 2.2 Fraud Scoring & Detection
- **FR-04:** The system shall score every valid transaction using an ML ensemble model within 80ms of ingestion
- **FR-05:** The scoring model shall produce a `fraud_score` (float, 0.0–1.0) and a `risk_tier` classification (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
- **FR-06:** The system shall apply configurable rule-based pre-filters (velocity checks, geo-velocity, blacklist matching) before ML scoring to reduce model load
- **FR-07:** The system shall correlate transaction signals with account behavioural profiles (spending patterns, device history, typical merchant categories)

### 2.3 Decision Engine
- **FR-08:** The system shall make an automated decision for each transaction: `APPROVE`, `SOFT_DECLINE` (challenge the customer), or `HARD_BLOCK`
- **FR-09:** Decision thresholds shall be configurable per customer risk tier (Standard, Premium, Business)
- **FR-10:** For `SOFT_DECLINE` decisions, the system shall trigger a step-up authentication challenge (OTP / biometric prompt) via the Notification Service

### 2.4 Case Management
- **FR-11:** Transactions with `HIGH` or `CRITICAL` risk tier shall automatically generate a fraud case in the Case Management Service
- **FR-12:** Fraud analysts shall be able to review, investigate, confirm, or dismiss cases via the Analyst Dashboard
- **FR-13:** Confirmed fraud cases shall be automatically fed back into the ML training pipeline as labelled data

### 2.5 Customer & Merchant Notifications
- **FR-14:** Customers shall receive real-time push notifications and/or SMS alerts for `SOFT_DECLINE` and `HARD_BLOCK` decisions
- **FR-15:** The system shall expose a REST API for customers to dispute blocked transactions

### 2.6 MLOps & Model Management
- **FR-16:** The system shall support automated model retraining triggered by accumulation of a configurable number of new labelled fraud samples (default: 500)
- **FR-17:** New model versions shall be evaluated against a holdout validation set before promotion to production
- **FR-18:** Model versioning, experiment tracking, and deployment history shall be managed via MLflow

### 2.7 Audit & Compliance
- **FR-19:** Every fraud decision shall be logged with a full audit trail including: input features, model version used, rule triggers, final decision, and timestamp
- **FR-20:** The system shall generate SHAP-based explainability reports for every `SOFT_DECLINE` and `HARD_BLOCK` decision
- **FR-21:** Audit logs shall be tamper-evident and retained for a minimum of 7 years per regulatory requirements

---

## 3. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Performance | End-to-end fraud decision latency ≤ 100ms at P99 |
| NFR-02 | Throughput | System shall handle ≥ 10,000 transactions per second (TPS) at peak |
| NFR-03 | Availability | Core detection pipeline shall maintain 99.99% uptime (≤ 52 minutes downtime/year) |
| NFR-04 | Scalability | All microservices shall scale horizontally via Kubernetes HPA |
| NFR-05 | Security | All inter-service communication encrypted via mTLS; all external APIs secured via OAuth 2.0 + JWT |
| NFR-06 | Data Privacy | PII fields (account number, device fingerprint) shall be tokenised at ingestion; raw PII never persisted in ML feature store |
| NFR-07 | Explainability | 100% of block/decline decisions shall have a SHAP explainability report generated |
| NFR-08 | Auditability | Audit log writes shall be synchronous and confirmed before decision response is returned |
| NFR-09 | Resilience | Kafka consumer groups shall implement dead-letter queue handling and retry logic with exponential backoff |
| NFR-10 | Observability | All services shall emit OpenTelemetry traces, Prometheus metrics, and structured JSON logs |

---

## 4. Use Cases

### UC-01: Real-Time Transaction Scoring
**Actor:** Payment Processor (External System)
**Precondition:** Transaction event published to Kafka topic
**Flow:**
1. Ingestion Service consumes event and validates schema
2. Feature Engineering Service enriches event with account profile and velocity metrics
3. ML Scoring Service runs ensemble model inference
4. Decision Engine applies thresholds and returns decision
5. Audit Service logs full decision trail
6. Response published to `transactions.decisions` Kafka topic
**Postcondition:** Transaction approved, soft-declined, or blocked within 100ms

### UC-02: Fraud Analyst Case Review
**Actor:** Fraud Analyst
**Flow:**
1. Analyst logs into Case Management Dashboard
2. Views queue of `HIGH`/`CRITICAL` risk cases
3. Drills into case - views transaction details, SHAP explanation, account history
4. Confirms fraud or dismisses case
5. System updates fraud label and queues sample for model retraining

### UC-03: Model Retraining Cycle
**Actor:** MLOps Scheduler (Automated)
**Flow:**
1. Airflow DAG triggers when labelled sample buffer reaches threshold
2. Training pipeline fetches new labelled data from Feature Store
3. Ensemble model retrained; evaluated on holdout set
4. If precision/recall targets met → model promoted to staging, then production
5. MLflow logs experiment, metrics, and model artifact

### UC-04: Customer Transaction Dispute
**Actor:** Customer (Mobile App User)
**Flow:**
1. Customer receives block notification
2. Opens app, navigates to dispute portal
3. Submits dispute with optional supporting information
4. Case created and assigned to fraud analyst queue
5. Resolution communicated to customer within SLA

---

## 5. Data Models

### 5.1 Transaction Event (Kafka Payload)
```json
{
  "transaction_id": "txn_9f3a2c1b",
  "account_id": "acc_token_8821",
  "merchant_id": "mch_4412",
  "merchant_category_code": "5411",
  "amount": 2350.00,
  "currency": "ZAR",
  "timestamp": "2026-03-15T10:45:22.341Z",
  "channel": "CNP_ONLINE",
  "device_fingerprint_token": "dfp_token_cc91",
  "ip_address_hash": "sha256:a3f9...",
  "geolocation": { "lat": -33.9249, "lon": 18.4241 },
  "is_international": false
}
```

### 5.2 Fraud Decision Record (PostgreSQL)
```sql
CREATE TABLE fraud_decisions (
    decision_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id      VARCHAR(64) NOT NULL,
    account_id_token    VARCHAR(64) NOT NULL,
    fraud_score         DECIMAL(5,4) NOT NULL,
    risk_tier           VARCHAR(16) NOT NULL,
    decision            VARCHAR(16) NOT NULL,   -- APPROVE / SOFT_DECLINE / HARD_BLOCK
    model_version       VARCHAR(32) NOT NULL,
    rule_triggers       JSONB,
    shap_report_ref     VARCHAR(256),
    decided_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processing_ms       INTEGER NOT NULL
);
```

### 5.3 Account Behavioural Profile (Redis Cache + Cassandra)
```json
{
  "account_id_token": "acc_token_8821",
  "avg_txn_amount_30d": 850.00,
  "typical_merchant_categories": ["5411", "5812", "7011"],
  "typical_geolocations": [
    { "city": "Cape Town", "country": "ZA" }
  ],
  "known_device_tokens": ["dfp_token_cc91", "dfp_token_aa04"],
  "velocity_1hr": 3,
  "velocity_24hr": 12,
  "last_international_txn": null,
  "risk_tier_override": null
}
```

---

## 6. Constraints & Assumptions

- All monetary values are handled as `DECIMAL(19,4)` - never floating point - to prevent precision errors
- The system assumes all external payment systems can publish to Kafka topics (or have an adapter layer)
- GDPR/POPIA compliance requires that all PII is tokenised before entering the ML pipeline - the tokenisation happens at the Ingestion Service boundary
- The system is designed for South African FinTech regulatory context (POPIA, FSCA requirements) but the architecture is jurisdiction-agnostic
- Initial ML models are trained on the IEEE-CIS Fraud Detection dataset for academic purposes; production would require institution-specific training data

---

*SentinelPay SPECIFICATION.md - Version 1.0 | 14 March 2026*
