# activity_diagrams.md - Activity Workflow Diagrams
## SentinelPay: Real-Time Fraud Detection & Prevention Engine

> **Assignment 8 - Activity Workflow Modeling**
> Notation: Mermaid flowchart (UML Activity Diagram standard)
> Swimlanes represented using subgraph blocks
> Builds on: Assignment 4 (SRD.md), Assignment 5 (USE_CASE_SPECIFICATIONS.md)


## Notation Key

| Symbol | Meaning |
|---|---|
| `([Start])` | Initial node (filled circle) |
| `([End])` | Final node (filled circle with ring) |
| Rectangle `[]` | Action node |
| Diamond `{}` | Decision node |
| `subgraph` blocks | Swimlanes (actor responsibility) |
| `==>` on fork/join | Parallel flow (fork and join bars) |

## Workflow 1 - Transaction Ingestion and PII Tokenisation

**Actors:** Payment Processor, Ingestion Service, Token Vault, Kafka

```mermaid
flowchart TD
    Start([Start]) --> PP_Publish

    subgraph PaymentProcessor["Payment Processor"]
        PP_Publish[Publish transaction JSON to transactions.raw]
    end

    subgraph IngestionService["Transaction Ingestion Service"]
        IS_Consume[Consume event from transactions.raw]
        IS_Validate{All mandatory fields present?}
        IS_DeadLetter[Route to transactions.dlq with error payload]
        IS_Tokenise[Send PII fields to Token Vault]
        IS_Enrich[Enrich with threat intelligence signals]
        IS_Publish[Publish tokenised event to transactions.enriched]
    end

    subgraph TokenVault["Token Vault Service"]
        TV_Tokenise[Generate opaque tokens for account_id, device_fingerprint, ip_address]
        TV_Return[Return token references]
    end

    subgraph KafkaBus["Apache Kafka"]
        K_DLQ[transactions.dlq]
        K_Enriched[transactions.enriched]
    end

    PP_Publish --> IS_Consume
    IS_Consume --> IS_Validate
    IS_Validate -- No --> IS_DeadLetter
    IS_DeadLetter --> K_DLQ
    K_DLQ --> End_Reject([End])
    IS_Validate -- Yes --> IS_Tokenise
    IS_Tokenise --> TV_Tokenise
    TV_Tokenise --> TV_Return
    TV_Return --> IS_Enrich
    IS_Enrich --> IS_Publish
    IS_Publish --> K_Enriched
    K_Enriched --> End([End])
```

**Explanation:**
This workflow maps to FR-01 (transaction ingestion), FR-02 (schema validation), and FR-03 (PII tokenisation). The decision node at schema validation creates two parallel paths: the rejection path routes to the dead-letter queue with a structured error payload, satisfying the Compliance Officer's requirement that all failed events are traceable. The tokenisation step is a mandatory sequential action before any downstream processing - raw PII never reaches Kafka. This addresses the Financial Regulator's concern about POPIA compliance. The workflow directly implements sprint tasks T-001 through T-009 from AGILE_PLANNING.md.

## Workflow 2 - ML Ensemble Fraud Scoring

**Actors:** Feature Engineering Service, ML Scoring Service (XGBoost, Isolation Forest, DistilBERT), Ensemble Aggregator, Kafka

```mermaid
flowchart TD
    Start([Start]) --> FE_Consume

    subgraph FeatureEngineering["Feature Engineering Service"]
        FE_Consume[Consume enriched event from transactions.enriched]
        FE_QueryRedis[Query Redis for account velocity counters]
        FE_QueryCassandra[Query Cassandra for 30-day amount baseline]
        FE_BuildVector[Build ML feature vector]
        FE_ValidateSchema{Feature vector schema valid?}
        FE_DeadLetter[Route to transactions.dlq - FEATURE_SCHEMA_MISMATCH]
        FE_Publish[Publish feature vector to transactions.features]
    end

    subgraph MLScoring["ML Scoring Service"]
        MS_Consume[Consume feature vector]
        MS_CheckCB{Circuit breaker OPEN?}
        MS_Fallback[Apply rule-only fallback scoring]

        MS_XGB[XGBoost Scorer - tabular fraud probability]
        MS_ISO[Isolation Forest Scorer - structural anomaly]
        MS_BERT[DistilBERT Scorer - merchant text risk]

        MS_Aggregate[Ensemble Aggregator - weighted average 60/25/15]
        MS_MapTier[Map fraud_score to risk_tier]
        MS_Publish[Publish scored result to transactions.scored]
    end

    FE_Consume --> FE_QueryRedis
    FE_Consume --> FE_QueryCassandra
    FE_QueryRedis --> FE_BuildVector
    FE_QueryCassandra --> FE_BuildVector
    FE_BuildVector --> FE_ValidateSchema
    FE_ValidateSchema -- No --> FE_DeadLetter --> End_DLQ([End])
    FE_ValidateSchema -- Yes --> FE_Publish
    FE_Publish --> MS_Consume
    MS_Consume --> MS_CheckCB
    MS_CheckCB -- Yes --> MS_Fallback --> MS_Publish
    MS_CheckCB -- No --> MS_XGB & MS_ISO & MS_BERT
    MS_XGB --> MS_Aggregate
    MS_ISO --> MS_Aggregate
    MS_BERT --> MS_Aggregate
    MS_Aggregate --> MS_MapTier
    MS_MapTier --> MS_Publish
    MS_Publish --> End([End])
```

**Explanation:**
This workflow is the most architecturally significant in SentinelPay. The parallel fork after the circuit breaker check shows the three ML models (XGBoost, Isolation Forest, DistilBERT) executing concurrently - this is the parallel actions requirement from the assignment brief. All three model outputs must complete before the Ensemble Aggregator can proceed (join bar). The circuit breaker decision node creates a fallback path that degrades gracefully to rule-only scoring when all models are unavailable. This addresses the ML Engineer's concern about system resilience from STAKEHOLDER_ANALYSIS.md. The concurrent Redis and Cassandra queries at the start are also parallel actions - both data sources are queried simultaneously to minimise latency within the 100ms SLA (NFR-P1).

## Workflow 3 - Fraud Decision Enforcement and Notification

**Actors:** Decision Engine, Notification Orchestrator, Notification Gateway, Audit Service, Customer

```mermaid
flowchart TD
    Start([Start]) --> DE_Consume

    subgraph DecisionEngine["Decision Engine"]
        DE_Consume[Consume scored transaction from transactions.scored]
        DE_GetTier[Retrieve account tier - Standard/Premium/Business]
        DE_CheckPrefilter{Pre-filter blacklist match?}
        DE_ApplyThreshold{Apply tier thresholds to fraud_score}
        DE_Approve[Decision = APPROVE]
        DE_SoftDecline[Decision = SOFT_DECLINE]
        DE_HardBlock[Decision = HARD_BLOCK]
        DE_Persist[Persist decision record to PostgreSQL]
        DE_Publish[Publish to transactions.decisions]
    end

    subgraph NotificationOrchestrator["Notification Orchestrator"]
        NO_Consume[Consume SOFT_DECLINE or HARD_BLOCK event]
        NO_Format[Format human-readable notification payload]
        NO_Dispatch[Dispatch to Notification Gateway]
    end

    subgraph NotificationGateway["External Notification Gateway"]
        NG_Send[Deliver push notification or SMS to customer]
        NG_Confirm{Delivery confirmed?}
        NG_Retry[Retry up to 3 times with exponential backoff]
    end

    subgraph AuditService["Audit Service"]
        AS_Consume[Consume all decision events from audit.events]
        AS_Hash[Compute HMAC-SHA256 record_hash]
        AS_Write[Write tamper-evident audit record to PostgreSQL]
    end

    subgraph Customer["Bank Customer"]
        C_Receive[Receive fraud alert notification]
    end

    DE_Consume --> DE_GetTier
    DE_GetTier --> DE_CheckPrefilter
    DE_CheckPrefilter -- Yes --> DE_HardBlock
    DE_CheckPrefilter -- No --> DE_ApplyThreshold
    DE_ApplyThreshold -- score < LOW --> DE_Approve
    DE_ApplyThreshold -- LOW <= score < HIGH --> DE_SoftDecline
    DE_ApplyThreshold -- score >= HIGH --> DE_HardBlock

    DE_Approve --> DE_Persist
    DE_SoftDecline --> DE_Persist
    DE_HardBlock --> DE_Persist
    DE_Persist --> DE_Publish

    DE_Publish --> NO_Consume & AS_Consume

    NO_Consume --> NO_Format
    NO_Format --> NO_Dispatch
    NO_Dispatch --> NG_Send
    NG_Send --> NG_Confirm
    NG_Confirm -- Yes --> C_Receive --> End_Notify([End])
    NG_Confirm -- No --> NG_Retry --> NG_Send

    AS_Consume --> AS_Hash
    AS_Hash --> AS_Write --> End_Audit([End])
```

**Explanation:**
This workflow shows parallel actions after the decision is published: the Notification Orchestrator and the Audit Service both consume the decision event simultaneously from their respective Kafka consumer groups. This parallel execution ensures that audit logging does not block or delay notification delivery - both happen independently. The pre-filter check at the start creates a short-circuit path that bypasses ML threshold evaluation for blacklisted merchants (FR-06). The notification delivery loop with retry models NFR-P2 (notification delivery reliability). This workflow addresses the Bank Customer's primary concern from STAKEHOLDER_ANALYSIS.md: knowing immediately when a transaction is blocked (FR-11).

## Workflow 4 - Step-Up Authentication Challenge

**Actors:** Notification Orchestrator, Customer, Step-Up Auth API, Decision Engine

```mermaid
flowchart TD
    Start([Start - SOFT_DECLINE decision received]) --> NO_GenerateOTP

    subgraph NotificationOrchestrator["Notification Orchestrator"]
        NO_GenerateOTP[Generate 6-digit cryptographic OTP]
        NO_StoreRedis[Store OTP in Redis with 120-second TTL]
        NO_Notify[Dispatch OTP notification to customer]
    end

    subgraph Customer["Bank Customer"]
        C_Receive[Receive OTP via push or SMS]
        C_Submit[Submit OTP via banking app]
    end

    subgraph StepUpAuthAPI["Step-Up Auth API"]
        SA_Receive[Receive OTP submission - POST /v1/auth/step-up]
        SA_CheckExpiry{OTP expired in Redis?}
        SA_CheckMatch{OTP matches stored value?}
        SA_IncrAttempt[Increment attempt counter]
        SA_CheckAttempts{Attempt count >= 3?}
        SA_Approve[Update transaction decision to APPROVE]
        SA_Escalate[Escalate transaction decision to HARD_BLOCK]
    end

    subgraph DecisionEngine["Decision Engine"]
        DE_UpdateApprove[Publish updated APPROVE decision]
        DE_UpdateBlock[Publish updated HARD_BLOCK decision]
    end

    NO_GenerateOTP --> NO_StoreRedis
    NO_StoreRedis --> NO_Notify
    NO_Notify --> C_Receive
    C_Receive --> C_Submit
    C_Submit --> SA_Receive
    SA_Receive --> SA_CheckExpiry
    SA_CheckExpiry -- Yes - expired --> SA_Escalate
    SA_CheckExpiry -- No --> SA_CheckMatch
    SA_CheckMatch -- Yes --> SA_Approve
    SA_CheckMatch -- No --> SA_IncrAttempt
    SA_IncrAttempt --> SA_CheckAttempts
    SA_CheckAttempts -- Yes --> SA_Escalate
    SA_CheckAttempts -- No --> C_Submit
    SA_Approve --> DE_UpdateApprove --> End_Approve([End - Transaction Approved])
    SA_Escalate --> DE_UpdateBlock --> End_Block([End - Transaction Hard Blocked])
```

**Explanation:**
This workflow models the complete step-up authentication lifecycle from FR-08 and UC5. The two decision nodes (OTP expired and OTP matches) create three distinct outcomes: immediate escalation on expiry, approval on correct submission, and a loopback to re-submission on incorrect OTP (up to the attempt limit). The loopback path is a key workflow feature - it shows the retry loop that allows customers up to 3 attempts before being blocked. This addresses the Bank Customer's concern about not being immediately hard-blocked for simple input errors. The Redis TTL acts as a hard deadline that the system enforces automatically. This workflow is traceable to US-005 (step-up authentication user story) and T-019 in the Sprint 1 backlog.

## Workflow 5 - Fraud Analyst Case Review and Resolution

**Actors:** Fraud Analyst, Case Management Service, SHAP Engine, ML Retraining Pipeline

```mermaid
flowchart TD
    Start([Start]) --> AN_Login

    subgraph FraudAnalyst["Fraud Analyst"]
        AN_Login[Login to Fraud Analyst Dashboard]
        AN_ViewQueue[View prioritised case queue - P1 first]
        AN_SelectCase[Select case to review]
        AN_ReviewEvidence[Review transaction details and account history]
        AN_ViewSHAP[View SHAP explainability report]
        AN_Decide{Resolve as?}
        AN_SubmitConfirmed[Submit CONFIRMED_FRAUD with investigation note]
        AN_SubmitDismissed[Submit FALSE_POSITIVE with mandatory note]
    end

    subgraph CaseManagementService["Case Management Service"]
        CM_LoadQueue[Return prioritised case queue within 2 seconds]
        CM_LoadDetail[Load case detail - transaction, account history, SHAP ref]
        CM_CheckSHAP{SHAP report ready?}
        CM_WaitSHAP[Display - Generating explanation, polling every 3 seconds]
        CM_PersistResolution[Persist resolution to PostgreSQL within 1 second]
        CM_UpdateStatus[Update case status - CONFIRMED or DISMISSED]
    end

    subgraph SHAPEngine["SHAP Explainability Engine"]
        SE_Compute[Compute SHAP values for top 5 features]
        SE_Format[Format as human-readable bar chart labels]
    end

    subgraph MLRetrainingPipeline["MLOps Retraining Pipeline"]
        ML_PublishLabel[Publish labelled fraud sample to fraud.labels topic]
        ML_CheckBuffer{Label buffer >= 500 samples?}
        ML_TriggerRetrain[Trigger Airflow retraining DAG]
    end

    AN_Login --> CM_LoadQueue
    CM_LoadQueue --> AN_ViewQueue
    AN_ViewQueue --> AN_SelectCase
    AN_SelectCase --> CM_LoadDetail
    CM_LoadDetail --> AN_ReviewEvidence
    AN_ReviewEvidence --> CM_CheckSHAP
    CM_CheckSHAP -- No --> SE_Compute & CM_WaitSHAP
    SE_Compute --> SE_Format --> AN_ViewSHAP
    CM_WaitSHAP --> CM_CheckSHAP
    CM_CheckSHAP -- Yes --> AN_ViewSHAP
    AN_ViewSHAP --> AN_Decide
    AN_Decide -- CONFIRMED_FRAUD --> AN_SubmitConfirmed
    AN_Decide -- FALSE_POSITIVE --> AN_SubmitDismissed
    AN_SubmitConfirmed --> CM_PersistResolution
    AN_SubmitDismissed --> CM_PersistResolution
    CM_PersistResolution --> CM_UpdateStatus
    CM_UpdateStatus --> ML_PublishLabel
    ML_PublishLabel --> ML_CheckBuffer
    ML_CheckBuffer -- Yes --> ML_TriggerRetrain --> End_Retrain([End - Retraining triggered])
    ML_CheckBuffer -- No --> End([End - Label buffered])
```

**Explanation:**
This workflow models UC8 (Review and Resolve Fraud Case) and includes a parallel action in the SHAP loading path - while the system polls for the SHAP report, the Case Management Service continues to display case details (parallel wait and display). The SHAP polling loop with a 3-second interval models the alternative flow AF-01 from UC8 specifications. The downstream connection to the MLOps retraining pipeline shows how analyst decisions directly drive model improvement, addressing the ML Engineer's stakeholder concern about continuous learning. This workflow addresses the Fraud Analyst's primary concern from STAKEHOLDER_ANALYSIS.md: having enough evidence (SHAP explanation, account history, transaction details) to make a confident resolution decision.

## Workflow 6 - ML Model Retraining and Deployment

**Actors:** Apache Airflow, MLflow, ML Scoring Service, Platform Administrator

```mermaid
flowchart TD
    Start([Start - Label buffer threshold reached]) --> AF_Trigger

    subgraph ApacheAirflow["Apache Airflow - MLOps Pipeline"]
        AF_Trigger[DAG triggered - fetch confirmed fraud labels]
        AF_FetchLabels[Fetch labelled samples from fraud.labels topic]
        AF_FetchFeatures[Fetch feature vectors from Cassandra]
        AF_Split[Split into training 80% and holdout 20%]
        AF_TrainXGB[Train XGBoost model]
        AF_TrainISO[Train Isolation Forest model]
        AF_TrainBERT[Fine-tune DistilBERT model]
        AF_EvalEnsemble[Evaluate ensemble on holdout set]
        AF_CheckGate{precision >= 0.85 AND recall >= 0.80?}
        AF_RejectModel[Archive model as REJECTED with failure metrics]
        AF_RegisterStaging[Register model versions in MLflow as Staging]
        AF_Monitor[Monitor staging for 5 minutes]
        AF_CheckMonitor{Anomalies detected in monitoring window?}
        AF_RejectStaging[Rollback to previous Production model]
        AF_Promote[Promote model versions to Production in MLflow]
    end

    subgraph MLflowRegistry["MLflow Model Registry"]
        MF_Log[Log experiment metrics and artifacts]
    end

    subgraph MLScoringService["ML Scoring Service"]
        MS_Poll[Model Loader polls MLflow every 60 seconds]
        MS_Detect{New Production version detected?}
        MS_HotSwap[Hot-swap model in memory - zero scoring downtime]
        MS_LogSwap[Log hot-swap event with old and new version]
    end

    subgraph PlatformAdmin["Platform Administrator"]
        PA_Alert[Receive alert - model rejected or anomaly detected]
    end

    AF_Trigger --> AF_FetchLabels & AF_FetchFeatures
    AF_FetchLabels --> AF_Split
    AF_FetchFeatures --> AF_Split
    AF_Split --> AF_TrainXGB & AF_TrainISO & AF_TrainBERT
    AF_TrainXGB --> AF_EvalEnsemble
    AF_TrainISO --> AF_EvalEnsemble
    AF_TrainBERT --> AF_EvalEnsemble
    AF_EvalEnsemble --> MF_Log
    MF_Log --> AF_CheckGate
    AF_CheckGate -- No --> AF_RejectModel --> PA_Alert --> End_Rejected([End])
    AF_CheckGate -- Yes --> AF_RegisterStaging
    AF_RegisterStaging --> AF_Monitor
    AF_Monitor --> AF_CheckMonitor
    AF_CheckMonitor -- Yes --> AF_RejectStaging --> PA_Alert
    AF_CheckMonitor -- No --> AF_Promote
    AF_Promote --> MS_Poll
    MS_Poll --> MS_Detect
    MS_Detect -- No --> MS_Poll
    MS_Detect -- Yes --> MS_HotSwap
    MS_HotSwap --> MS_LogSwap --> End([End - New model serving])
```

**Explanation:**
This workflow is the richest in parallel actions. Three training jobs (XGBoost, Isolation Forest, DistilBERT) execute concurrently in the Airflow DAG, and two data fetch operations (labels and feature vectors) also run in parallel at the start. The evaluation gate (precision AND recall thresholds) is a hard guard condition - failing either metric alone is sufficient to reject the model. The 5-minute staging monitoring window creates a time-bound observation phase before production promotion. This workflow addresses the ML Engineer's success metric from STAKEHOLDER_ANALYSIS.md: "new model version deployable to staging within 2 hours of training completion" and "automated rollback within 5 minutes of degradation detection."

## Workflow 7 - Customer Transaction Dispute

**Actors:** Bank Customer, Dispute API, Case Management Service, Fraud Analyst

```mermaid
flowchart TD
    Start([Start]) --> C_Navigate

    subgraph BankCustomer["Bank Customer"]
        C_Navigate[Navigate to blocked transaction in portal]
        C_SelectDispute[Select Dispute this transaction]
        C_EnterNote[Optionally enter supporting note]
        C_Submit[Submit dispute - POST /v1/disputes]
        C_ReceiveConfirm[Receive dispute_id and 48-hour SLA confirmation]
    end

    subgraph DisputeAPI["Customer Dispute API"]
        DA_Validate{Transaction exists AND HARD_BLOCKED?}
        DA_CheckWindow{Within 30-day dispute window?}
        DA_CheckDuplicate{Prior dispute exists for transaction_id?}
        DA_Return404[Return HTTP 404 - transaction not eligible]
        DA_Return422[Return HTTP 422 - dispute window expired]
        DA_Return409[Return HTTP 409 - duplicate dispute with existing dispute_id]
        DA_CreateRecord[Create dispute record in PostgreSQL with status OPEN]
        DA_Return201[Return HTTP 201 with dispute_id and resolution timeline]
    end

    subgraph CaseManagementService["Case Management Service"]
        CM_CreateCase[Create or link fraud investigation case]
        CM_AssignPriority[Assign priority based on original fraud_score]
        CM_NotifyQueue[Notify fraud analyst queue]
    end

    subgraph FraudAnalyst["Fraud Analyst"]
        FA_Receive[Receive case assignment notification]
        FA_Review[Review dispute and transaction evidence]
        FA_Resolve{Resolution?}
        FA_ResolveTrue[Confirm fraud - customer claim rejected]
        FA_ResolveFalse[Confirm false positive - customer claim upheld]
        FA_NotifyCustomer[Notify customer of resolution within 48 hours SLA]
    end

    C_Navigate --> C_SelectDispute
    C_SelectDispute --> C_EnterNote
    C_EnterNote --> C_Submit
    C_Submit --> DA_Validate
    DA_Validate -- No --> DA_Return404 --> End_404([End])
    DA_Validate -- Yes --> DA_CheckWindow
    DA_CheckWindow -- No --> DA_Return422 --> End_422([End])
    DA_CheckWindow -- Yes --> DA_CheckDuplicate
    DA_CheckDuplicate -- Yes --> DA_Return409 --> End_409([End])
    DA_CheckDuplicate -- No --> DA_CreateRecord
    DA_CreateRecord --> DA_Return201 & CM_CreateCase
    DA_Return201 --> C_ReceiveConfirm --> End_Customer([End - Customer notified])
    CM_CreateCase --> CM_AssignPriority
    CM_AssignPriority --> CM_NotifyQueue
    CM_NotifyQueue --> FA_Receive
    FA_Receive --> FA_Review
    FA_Review --> FA_Resolve
    FA_Resolve -- Fraud confirmed --> FA_ResolveTrue
    FA_Resolve -- False positive --> FA_ResolveFalse
    FA_ResolveTrue --> FA_NotifyCustomer --> End_Fraud([End])
    FA_ResolveFalse --> FA_NotifyCustomer --> End_Clear([End])
```

**Explanation:**
This workflow shows parallel actions after the dispute record is created: the API returns HTTP 201 to the customer and the Case Management Service creates the linked case simultaneously. The customer receives confirmation without waiting for case creation to complete - this is important for the 1-second API response time requirement from FR-12. The three sequential validation decision nodes model the three alternative flows from UC7 specifications exactly: 404 for invalid transactions, 422 for expired windows, and 409 for duplicates. This workflow addresses the Bank Customer's success metric from STAKEHOLDER_ANALYSIS.md: "dispute resolution completed within 48 hours."

## Workflow 8 - Regulatory Audit Report Generation

**Actors:** Compliance Officer, Audit API, Audit Service, MinIO Object Store

```mermaid
flowchart TD
    Start([Start]) --> CO_Login

    subgraph ComplianceOfficer["Compliance Officer"]
        CO_Login[Login with Compliance Officer RBAC role]
        CO_SetParams[Set report parameters - date range, decision type filter]
        CO_Submit[Submit report request - POST /v1/audit/reports]
        CO_Wait{Report size large?}
        CO_WaitAsync[Wait for async notification]
        CO_Download[Download report - JSON or PDF]
    end

    subgraph AuditAPI["Audit Report API"]
        AA_Auth{Valid Compliance Officer JWT?}
        AA_Reject[Return HTTP 403 Forbidden]
        AA_CheckSize{Estimated record count > 100000?}
        AA_Return202[Return HTTP 202 Accepted with report_job_id]
        AA_Return200[Return HTTP 200 with report inline]
        AA_Route[Route to Audit Service]
    end

    subgraph AuditService["Audit Service"]
        AS_Fetch[Fetch audit records from PostgreSQL matching filter]
        AS_Verify{Integrity check - recompute HMAC-SHA256 for each record}
        AS_FlagTampered[Flag tampered records - raise P0 alert]
        AS_FetchSHAP[Fetch SHAP report references from MinIO]
        AS_Compile[Compile full report with metadata and decision records]
        AS_GeneratePDF[Generate PDF and JSON report formats]
    end

    subgraph MinIO["MinIO Object Store"]
        MO_Fetch[Return SHAP report documents for HARD_BLOCK decisions]
    end

    CO_Login --> CO_SetParams
    CO_SetParams --> CO_Submit
    CO_Submit --> AA_Auth
    AA_Auth -- Invalid --> AA_Reject --> End_403([End])
    AA_Auth -- Valid --> AA_CheckSize
    AA_CheckSize -- Yes --> AA_Return202 --> CO_Wait
    AA_CheckSize -- No --> AA_Route
    CO_Wait --> CO_WaitAsync --> CO_Download
    AA_Route --> AS_Fetch
    AS_Fetch --> AS_Verify
    AS_Verify -- Mismatch found --> AS_FlagTampered --> AS_Compile
    AS_Verify -- All verified --> AS_FetchSHAP
    AS_FetchSHAP --> MO_Fetch
    MO_Fetch --> AS_Compile
    AS_Compile --> AS_GeneratePDF
    AS_GeneratePDF --> CO_Download
    CO_Download --> End([End - Report delivered])
```

**Explanation:**
This workflow models UC11 (Generate Audit Report) and addresses the Financial Regulator's primary concern: producing verifiable evidence of fraud prevention activity on demand. The asynchronous path (HTTP 202) for large reports ensures the API does not timeout on multi-year date ranges. The integrity check decision node creates a parallel output - tampered records are flagged AND included in the report (not suppressed), which is a deliberate regulatory design decision: the Compliance Officer must see evidence of tampering, not have it hidden. The SHAP report fetching from MinIO adds the explainability layer that satisfies the POPIA requirement for explainable automated decisions. This workflow traces to FR-15 (Tamper-Evident Audit Logging), NFR-S3 (Data Encryption at Rest), and US-011 (Compliance Officer user story).

## Activity Diagrams Traceability Matrix

| Workflow | Key Actors | Parallel Actions | FR/NFR References | User Story |
|---|---|---|---|---|
| Transaction Ingestion and PII Tokenisation | Payment Processor, Ingestion Service, Token Vault | Redis + Cassandra queries in parallel | FR-01, FR-02, FR-03 | US-001, US-002, US-003 |
| ML Ensemble Fraud Scoring | Feature Engineering, ML Scoring (3 models), Kafka | XGBoost + ISO Forest + BERT run concurrently | FR-04, FR-05, NFR-P1 | US-004 |
| Fraud Decision Enforcement and Notification | Decision Engine, Notification Orchestrator, Audit Service | Notification + Audit consume decisions in parallel | FR-06, FR-07, FR-11, FR-15 | US-004, US-006, US-011 |
| Step-Up Authentication Challenge | Notification Orchestrator, Customer, Auth API | OTP generation + Redis storage | FR-08, FR-11 | US-005 |
| Fraud Analyst Case Review and Resolution | Fraud Analyst, Case Management, SHAP Engine, MLOps | SHAP computation + case display | FR-09, FR-10, FR-13 | US-008, US-009 |
| ML Model Retraining and Deployment | Airflow, MLflow, ML Scoring Service | 3 models train concurrently, 2 data fetches in parallel | FR-13, FR-14 | US-009, US-010 |
| Customer Transaction Dispute | Bank Customer, Dispute API, Case Management, Analyst | API response + case creation in parallel | FR-12 | US-007 |
| Regulatory Audit Report Generation | Compliance Officer, Audit API, Audit Service, MinIO | Async report path for large datasets | FR-15, NFR-S3, NFR-S4 | US-011 |

