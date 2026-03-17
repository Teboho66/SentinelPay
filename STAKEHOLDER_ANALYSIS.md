# STAKEHOLDER_ANALYSIS.md - SentinelPay: Real-Time Fraud Detection & Prevention Engine

> **Assignment 4 - Stakeholder Analysis**
> Building on Assignment 3 | SentinelPay FinTech Fraud Detection System

---

## Overview

This document identifies and analyses all key stakeholders for the SentinelPay system. A stakeholder is any individual, group, or organisation that has an interest in, is affected by, or has influence over the system and its outcomes.

Eight stakeholders have been identified across three categories:

| Category | Stakeholders |
|---|---|
| **Primary Users** | Bank Customer, Fraud Analyst, Platform Administrator |
| **Internal Organisational** | Compliance Officer, ML Engineer / Data Scientist |
| **External / Institutional** | Payment Processor Integration Team, Financial Regulator, Executive Leadership (CTO / CFO) |

---

## Stakeholder 1 - Bank Customer

| Attribute | Detail |
|---|---|
| **Role** | End-user of the banking platform. Initiates digital payments via mobile app or web portal. The primary subject of fraud protection - their transactions are scored in real time and they receive alerts and step-up challenges when suspicious activity is detected. |
| **Key Concerns** | Legitimate transactions must not be blocked. Fraud on their account must be caught before money is lost. When a transaction is blocked, they need to understand why and dispute it quickly. They do not want to be bombarded with false alerts that erode trust. |
| **Pain Points** | Legitimate purchases (especially high-value or international) are frequently declined by overly aggressive fraud rules, causing embarrassment and inconvenience. When fraud does occur, dispute resolution is slow and opaque. Real-time notification of genuine fraud is delayed. Customers receive no explanation for why a transaction was declined. |
| **Success Metrics** | False positive rate (legitimate transactions incorrectly blocked) reduced to below 0.5%. Genuine fraud detected and blocked before settlement in ≥ 95% of cases. Dispute resolution completed within 48 hours. Step-up authentication challenge completed in under 30 seconds. Customer satisfaction (CSAT) score for fraud handling ≥ 4.2 / 5.0. |
| **Influence Level** | High - customer churn and regulatory complaints directly impact business revenue |
| **Traceability** | FR-08, FR-10, FR-14, FR-15, NFR-U1, NFR-P1, NFR-P2 |

---

## Stakeholder 2 - Fraud Analyst

| Attribute | Detail |
|---|---|
| **Role** | Financial crime investigator employed by the bank or FinTech institution. Reviews cases automatically flagged by SentinelPay as HIGH or CRITICAL risk. Makes final human judgement calls - confirms fraud, dismisses false positives, escalates to law enforcement where appropriate. Also responsible for refining detection rules and providing feedback labels that retrain the ML models. |
| **Key Concerns** | The case queue must be prioritised by risk severity so they focus on genuine threats first. Every case must include enough evidence (transaction details, behavioural history, SHAP explanation) to make a confident decision without external research. False positives in the queue waste their time and reduce throughput on real fraud. Model decisions must be explainable so they can trust, challenge, or override the system. |
| **Pain Points** | Current tools surface hundreds of low-quality alerts per day, overwhelming analysts with noise. SHAP explanations are absent in legacy systems - analysts must reverse-engineer why a transaction was flagged. Case resolution is disconnected from model retraining, meaning confirmed fraud doesn't improve future detection. No SLA tracking on case resolution times. |
| **Success Metrics** | Case queue precision (proportion of queued cases that are genuine fraud) ≥ 70%. Time-to-resolution per case reduced by 40% compared to legacy system. 100% of queued cases include a SHAP explanation. Analyst-confirmed fraud labels fed back into retraining pipeline within 1 hour of resolution. Queue cleared of critical cases within 4 hours of generation. |
| **Influence Level** | High - analyst feedback directly drives ML model quality improvement |
| **Traceability** | FR-11, FR-12, FR-13, FR-19, FR-20, NFR-U2, NFR-M1 |

---

## Stakeholder 3 - Platform Administrator

| Attribute | Detail |
|---|---|
| **Role** | Technical staff member (DevOps / SRE) responsible for the operational health of SentinelPay. Manages Kubernetes deployments, monitors service health, configures system thresholds and rules, manages ML model promotion between staging and production, and responds to incidents. |
| **Key Concerns** | System uptime and reliability - any downtime on the fraud detection pipeline means unscored transactions are either blindly approved (fraud risk) or blindly blocked (customer impact). Deployments must be zero-downtime. Configuration changes (threshold updates, rule modifications) must be auditable. |
| **Pain Points** | Legacy fraud systems require service restarts to update rules or thresholds, causing brief outages. No centralised observability - diagnosing latency spikes requires jumping between multiple unconnected log systems. ML model deployments are manual and error-prone, with no automated rollback on performance degradation. |
| **Success Metrics** | System availability ≥ 99.99% (≤ 52 minutes unplanned downtime per year). Zero-downtime deployments for 100% of releases. Mean time to detect (MTTD) incidents ≤ 2 minutes via Prometheus/Grafana alerting. Mean time to recover (MTTR) from incidents ≤ 15 minutes. All configuration changes logged in immutable audit trail. |
| **Influence Level** | Medium-High - controls deployment pipeline and operational configuration |
| **Traceability** | NFR-D1, NFR-D2, NFR-M2, NFR-SC1, NFR-O1 |

---

## Stakeholder 4 — Compliance Officer

| Attribute | Detail |
|---|---|
| **Role** | Regulatory and legal risk specialist responsible for ensuring SentinelPay operates within the bounds of applicable financial crime and data protection legislation. In the South African context this includes POPIA (Protection of Personal Information Act), FSCA (Financial Sector Conduct Authority) requirements, and internationally GDPR and PSD2. Responsible for regulatory reporting, audit submissions, and managing the institution's relationship with regulators. |
| **Key Concerns** | Every automated financial decision that affects a customer must be explainable and auditable on demand. PII must not be exposed in ML pipelines or logs. Audit records must be tamper-evident and retained for the legally required period (7 years minimum under South African financial law). The system must produce evidence of fraud prevention activity for regulatory examinations. |
| **Pain Points** | Current black-box ML models produce decisions that cannot be explained to regulators or customers - a direct POPIA and GDPR compliance risk. Audit logs are scattered across multiple systems with no unified trail. PII is processed in ML pipelines without proper tokenisation. No automated regulatory reporting capability. |
| **Success Metrics** | 100% of HARD_BLOCK and SOFT_DECLINE decisions accompanied by a SHAP explainability report retrievable within 5 seconds on demand. Zero PII present in ML feature vectors or model training data (verified by quarterly automated scans). Audit logs retained for 7 years with tamper-evident cryptographic verification. Regulatory examination preparedness: full audit trail retrievable for any decision within 24 hours of request. Zero regulatory findings related to SentinelPay in annual FSCA examination. |
| **Influence Level** | High - non-compliance can result in regulatory sanctions, fines, and licence revocation |
| **Traceability** | FR-19, FR-20, FR-21, NFR-S3, NFR-S4, NFR-M1 |

---

## Stakeholder 5 - ML Engineer / Data Scientist

| Attribute | Detail |
|---|---|
| **Role** | Technical specialist responsible for designing, training, evaluating, and maintaining the fraud detection ML models (XGBoost, Isolation Forest, DistilBERT). Manages the MLOps pipeline, feature engineering logic, model performance monitoring, and the continuous retraining cycle. Works closely with fraud analysts to understand detection gaps and with the platform team on model deployment. |
| **Key Concerns** | Model performance must be measurable and monitored continuously - degradation in precision or recall must trigger alerts before it affects detection quality. The retraining pipeline must be automated and reliable. Feature engineering logic must be reproducible and version-controlled. Experiment tracking must enable comparison of model versions. The system must support rapid iteration - new model architectures must be testable without disrupting production. |
| **Pain Points** | Manual model deployment processes are slow and error-prone. No standardised feature store means feature definitions drift between training and serving environments (training-serving skew). Lack of automated model performance monitoring means degradation is only detected after analyst complaints. No A/B testing infrastructure for comparing model versions in production. |
| **Success Metrics** | Model retraining cycle fully automated with zero manual steps required for standard retraining runs. Training-serving feature skew: zero discrepancy between training features and serving features (enforced by shared feature definitions). Model performance monitored in real time: precision and recall metrics updated every 15 minutes. New model version deployable to staging within 2 hours of training completion. Automated rollback triggered within 5 minutes if new model version causes precision drop ≥ 5% vs baseline. |
| **Influence Level** | High - directly controls the quality and accuracy of fraud detection |
| **Traceability** | FR-16, FR-17, FR-18, NFR-M2, NFR-M3, NFR-SC2 |

---

## Stakeholder 6 - Payment Processor Integration Team

| Attribute | Detail |
|---|---|
| **Role** | Technical team at the external payment processor organisation (e.g., Visa, Mastercard, PayShap) responsible for integrating their transaction submission systems with SentinelPay's ingestion API. They publish transaction events to SentinelPay and consume fraud decisions. They are external to the institution but are critical infrastructure partners. |
| **Key Concerns** | SentinelPay's Kafka ingestion API must have a stable, versioned, well-documented schema. Decision response latency must be predictable - they have SLAs with their own downstream systems. Any breaking change to the transaction event schema or decision format must be communicated and versioned with backward compatibility. System availability directly affects their ability to process payments. |
| **Pain Points** | Undocumented or frequently changing API schemas force repeated integration rework. Poor latency SLAs from fraud systems cause timeouts in payment processing flows. Lack of a test/sandbox environment makes it impossible to validate integration changes before going live. No webhook or event-driven mechanism for receiving decision notifications. |
| **Success Metrics** | API schema versioning: zero breaking changes without minimum 30-day deprecation notice. Integration documentation rated "complete and accurate" by external integration teams in quarterly review. Sandbox environment available 99.9% of the time for integration testing. Decision response latency P95 ≤ 80ms as measured from the processor's ingestion point. |
| **Influence Level** | Medium - a critical integration partner whose cooperation is required for the system to function |
| **Traceability** | FR-01, FR-02, FR-03, NFR-P1, NFR-D2, NFR-M1 |

---

## Stakeholder 7 - Financial Regulator (FSCA / Reserve Bank)

| Attribute | Detail |
|---|---|
| **Role** | External governmental authority - in South Africa, the Financial Sector Conduct Authority (FSCA) and the South African Reserve Bank (SARB) - that oversees the institution's compliance with financial crime prevention obligations. Does not interact with the system directly but examines audit records, requests reports, and enforces compliance through regulatory examinations and potential sanctions. |
| **Key Concerns** | The institution must demonstrate that effective fraud prevention controls are in place and operating. Automated decision-making systems must not discriminate against customers unlawfully. PII processing must comply with POPIA. The institution must be able to provide evidence of fraud prevention activity and explain specific automated decisions upon request. AML obligations must be met. |
| **Pain Points** | Institutions frequently cannot produce coherent explanations for individual automated fraud decisions during examinations. Audit trails are incomplete or stored in formats that are not regulatorily admissible. Lack of standardised fraud reporting makes cross-institution comparison difficult. |
| **Success Metrics** | Full regulatory audit trail for any specific transaction decision producible within 24 hours of regulator request. Zero POPIA violations identified in annual data protection audit. AML suspicious activity reporting: 100% of flagged cases escalated to compliance officer within regulatory reporting deadlines. Regulatory examination outcome: zero material findings related to fraud system operation. |
| **Influence Level** | Very High - regulatory non-compliance can result in financial penalties, licence suspension, or forced operational changes |
| **Traceability** | FR-19, FR-20, FR-21, NFR-S3, NFR-S4 |

---

## Stakeholder 8 — Executive Leadership (CTO / CFO)

| Attribute | Detail |
|---|---|
| **Role** | Senior organisational decision-makers who commissioned SentinelPay and are accountable for its business outcomes. The CTO is responsible for technical strategy and system reliability. The CFO is responsible for the financial impact of fraud losses, false positive costs, and the return on investment of the fraud prevention platform. Both require high-level visibility into system performance without operational detail. |
| **Key Concerns** | Fraud losses must be measurably reduced year-on-year. False positive rates that block legitimate revenue must be minimised. The system must be cost-effective to operate at scale. Regulatory compliance must be maintained to avoid sanctions. The platform must be able to evolve with the business - new channels, new products, and new fraud vectors must be accommodatable without full rebuilds. |
| **Pain Points** | Lack of real-time business-level KPI dashboards - leadership cannot see fraud loss trends, false positive impact on revenue, or detection rate improvements without requesting manual reports. Uncertainty about the ROI of fraud prevention investment. No clear view of regulatory exposure from current system gaps. |
| **Success Metrics** | Fraud loss rate reduced by ≥ 30% within 12 months of SentinelPay deployment. False positive revenue impact reduced by ≥ 25% vs legacy system. System operating cost per 1,000 transactions reduced vs legacy batch system. Executive KPI dashboard updated in real time. Zero material regulatory findings in first post-deployment examination. |
| **Influence Level** | Very High - budget authority and strategic direction |
| **Traceability** | NFR-SC1, NFR-SC2, NFR-P2, NFR-O1 |

---

## Stakeholder Summary Table

| # | Stakeholder | Category | Influence Level | Primary Concern |
|---|---|---|---|---|
| 1 | Bank Customer | Primary User | High | Low false positives; fast dispute resolution |
| 2 | Fraud Analyst | Primary User | High | Case quality; SHAP explainability; feedback loop |
| 3 | Platform Administrator | Primary User | Medium-High | System uptime; zero-downtime deployments |
| 4 | Compliance Officer | Internal | High | Regulatory audit trail; PII protection; POPIA |
| 5 | ML Engineer / Data Scientist | Internal | High | Model accuracy; automated MLOps; no training-serving skew |
| 6 | Payment Processor Integration Team | External | Medium | Stable API schema; latency SLAs; sandbox environment |
| 7 | Financial Regulator (FSCA / SARB) | External | Very High | Compliance evidence; explainability; AML reporting |
| 8 | Executive Leadership (CTO / CFO) | Internal | Very High | ROI; fraud loss reduction; regulatory risk |

---

## Stakeholder Conflict Analysis

Identifying where stakeholder needs create tensions is critical for requirements engineering. The following conflicts must be managed in the SentinelPay design:

| Conflict | Stakeholders | Resolution Approach |
|---|---|---|
| **Sensitivity vs Specificity** | Bank Customer (wants low false positives) vs Compliance Officer / Regulator (wants maximum fraud caught) | Configurable risk tier thresholds with separate tuning per channel. Accept higher false positive rate on high-risk channels (e.g., international CNP). |
| **Latency vs Explainability** | Payment Processor (wants ≤ 80ms decisions) vs Compliance Officer (wants full SHAP reports) | SHAP computation is asynchronous - decision is returned in real time, SHAP report is generated post-decision and stored for retrieval. |
| **Innovation Speed vs Stability** | ML Engineer (wants rapid model iteration) vs Payment Processor (wants stable API contracts) | Model changes are internal - they do not affect the external API schema. Model versions are hot-swapped without API changes. |
| **Cost Efficiency vs Availability** | Executive Leadership (wants low operating cost) vs Platform Administrator (wants 99.99% uptime) | Kubernetes HPA scales down during off-peak hours, maintaining baseline availability while reducing cost. |

---

*SentinelPay STAKEHOLDER_ANALYSIS.md - Version 1.0 | March 2026*