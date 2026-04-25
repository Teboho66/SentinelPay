## SentinelPay: Real-Time Fraud Detection & Prevention Engine

> **Assignment 9 - Domain Model**
> Builds on: Assignment 4 (SRD.md), Assignment 5 (USE_CASE_SPECIFICATIONS.md), Assignment 8 (state_diagrams.md)


## 1. Overview

The SentinelPay domain model captures the core business concepts of a real-time fraud detection system. These entities represent the key objects that the system creates, modifies, and reasons about during fraud detection operations. Each entity maps directly to functional requirements in SRD.md and state diagrams in Assignment 8.

**Domain:** FinTech - Digital Payments and Financial Crime Prevention

Seven core domain entities have been identified covering the complete fraud detection lifecycle: from transaction submission through ML scoring, decision enforcement, case management, audit compliance, and model improvement.


## 2. Domain Entities

| Entity | Key Attributes | Key Methods | Relationships | FR Mapping |
|---|---|---|---|---|
| **Transaction** | transactionId, accountIdToken, amount (BigDecimal), fraudScore, riskTier, decision, processingMs | validate(), tokenisePII(), computeFraudScore(), applyDecision() | Creates FraudCase, AuditRecord, StepUpChallenge; enriched by AccountProfile; scored by MLModel | FR-01 to FR-08 |
| **FraudCase** | caseId, fraudScore, priority (P1/P2/P3), status, shapReportRef, analystNote, slaBreachAt | assignToAnalyst(), resolve(), publishFraudLabel(), isBreachingSLA() | Composed from Transaction; linked to CustomerDispute; resolved by Fraud Analyst | FR-09, FR-10, FR-13 |
| **MLModel** | modelId, modelName, version, stage, precision, recall, f1Score, featureSchemaVersion | evaluate(), meetsPromotionGate(), promote(), score(), hotSwap() | Aggregated into EnsembleScorer (3 models); scores many Transactions | FR-13, FR-14 |
| **AuditRecord** | auditId, transactionId, decision, modelVersionComposite, ruleTriggers, shapReportRef, recordHash | computeHash(), verifyIntegrity(), toComplianceReport() | Created from Transaction (1-to-1); references SHAP report in object store | FR-15, NFR-S4 |
| **AccountProfile** | accountIdToken, velocity1hr/6hr/24hr, avgAmount30d, knownDeviceTokens, isNewAccount, riskTierOverride | computeGeoVelocity(), isNewDevice(), buildFeatureVector(), updateVelocity() | Associated with many Transactions; enriches each Transaction during scoring | FR-05 |
| **CustomerDispute** | disputeId, transactionId, status, submittedAt, resolutionSlaAt (48hrs) | validate(), linkToCase(), resolve(), isWithinDisputeWindow() | Associated with Transaction; linked to FraudCase | FR-12 |
| **StepUpChallenge** | challengeId, transactionId, otpHash, ttlSeconds (120), attemptCount, maxAttempts (3), status | generateOTP(), deliverToCustomer(), validateOTP(), escalateToHardBlock() | Composed from SOFT_DECLINE Transaction | FR-08, FR-11 |


## 3. Entity Descriptions

### Transaction
The primary input to the SentinelPay pipeline. Represents a financial payment event submitted by the Payment Processor for real-time fraud evaluation. The Transaction is the root entity from which all other entities are created. Amount is stored as BigDecimal(19,4) to prevent floating point precision errors in financial calculations. All PII fields (accountId, deviceFingerprint, ipAddress) are tokenised before any downstream processing per FR-03.

### FraudCase
An investigation case automatically created when a Transaction receives HARD_BLOCK with risk_tier HIGH or CRITICAL. Represents the unit of work for a Fraud Analyst. Priority is computed from fraudScore: P1 (>= 0.90), P2 (0.75-0.89), P3 (below 0.75). The slaBreachAt field is computed as createdAt + 4 hours, and an alert fires when a case is within 15 minutes of breaching this SLA.

### MLModel
A versioned model artifact in the MLflow registry. Represents one constituent model in the fraud detection ensemble (XGBoost, Isolation Forest, or DistilBERT). Lifecycle stages are TRAINING, STAGING, PRODUCTION, ARCHIVED, REJECTED. A model may only be promoted to Production if precision >= 0.85 AND recall >= 0.80 on the holdout validation set.

### AuditRecord
An immutable, tamper-evident log entry created synchronously for every fraud decision including APPROVE. The recordHash is an HMAC-SHA256 signature of all record fields. AuditRecord rows have DELETE privilege revoked at the PostgreSQL role level - no application code path can delete them. Retained for minimum 7 years per FSCA regulatory requirement.

### AccountProfile
A real-time behavioural profile maintained in Redis for sub-millisecond feature lookup during ML scoring. Tracks velocity metrics, spending patterns, and device history. Accounts with fewer than 10 transactions are classified as new accounts and receive population-average baselines with a risk boost applied to their fraudScore.

### CustomerDispute
A formal dispute submitted by a Bank Customer against a HARD_BLOCK decision. Subject to a 30-day dispute window and a 48-hour resolution SLA. Only HARD_BLOCK decisions are disputable - APPROVE and SOFT_DECLINE decisions are not eligible. Enforces uniqueness: only one dispute per transactionId (HTTP 409 on duplicate).

### StepUpChallenge
A one-time password challenge issued when a Transaction receives SOFT_DECLINE. OTP is stored as a bcrypt hash - never in plaintext. The Redis key is set with an atomic SET-with-TTL. After 3 failed attempts, the transaction is immediately escalated to HARD_BLOCK with no further OTP opportunities.

## 4. Business Rules (Key Selection)

| Rule ID | Entity | Business Rule |
|---|---|---|
| BR-T1 | Transaction | Amount stored as BigDecimal(19,4) - never float or double |
| BR-T2 | Transaction | PII tokenised before any downstream Kafka publication |
| BR-T5 | Transaction | End-to-end processing <= 100ms at P99 (NFR-P1) |
| BR-FC2 | FraudCase | FALSE_POSITIVE resolution requires non-empty analystNote |
| BR-FC3 | FraudCase | CONFIRMED_FRAUD publishes fraud label to MLOps within 60 seconds |
| BR-FC4 | FraudCase | fraudScore >= 0.90 = P1 priority regardless of creation time |
| BR-ML1 | MLModel | Promotion requires precision >= 0.85 AND recall >= 0.80 |
| BR-ML3 | MLModel | Feature schema version must match serving pipeline to prevent training-serving skew |
| BR-AR1 | AuditRecord | Write is synchronous - decision response held until record confirmed persisted |
| BR-AR2 | AuditRecord | DELETE privilege revoked at PostgreSQL role level |
| BR-AR3 | AuditRecord | Retained minimum 7 years per FSCA requirement |
| BR-AP1 | AccountProfile | transactionCount < 10 = new account risk boost applied to fraudScore |
| BR-AP2 | AccountProfile | Velocity updates must be atomic Redis operations to prevent race conditions |
| BR-CD2 | CustomerDispute | One dispute per transactionId - duplicate rejected HTTP 409 |
| BR-CD3 | CustomerDispute | Must be submitted within 30 calendar days of transaction |
| BR-SU2 | StepUpChallenge | OTP stored as bcrypt hash - never plaintext in Redis, database, or logs |
| BR-SU4 | StepUpChallenge | maxAttempts exceeded = immediate HARD_BLOCK with no further OTP opportunities |

---