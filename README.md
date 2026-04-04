# 🛡️ SentinelPay - Real-Time Fraud Detection & Prevention Engine

> **Postgraduate Software Engineering**
> **Author:** Teboho Mokoni

---

## What is SentinelPay?

SentinelPay is an intelligent, real-time fraud detection and prevention engine designed for modern financial institutions and FinTech platforms. It combines streaming transaction processing, machine learning inference, behavioural analytics, and automated response orchestration to identify and neutralise fraudulent activity **before it causes financial damage** - at sub-100ms latency, at scale.

In 2026, card-not-present fraud, identity spoofing, and AI-generated synthetic identity attacks are the dominant threat vectors in digital payments. SentinelPay is architected specifically to combat these threats using an event-driven microservices backbone, ensemble ML models (gradient boosting + transformer-based anomaly detection), and a feedback loop that continuously retrains on confirmed fraud signals.

### What SentinelPay Will Do Once Completed

- **Ingest** live transaction streams from payment processors, mobile wallets, and banking APIs via Kafka event pipelines
- **Score** every transaction in real time using a multi-model ML ensemble (XGBoost + Isolation Forest + fine-tuned DistilBERT for merchant text signals)
- **Enforce** automated rule-based and ML-driven decisions: approve, flag for review, or block - with configurable thresholds per customer risk tier
- **Alert** customers and fraud analysts instantly via push notification, SMS, and a case management dashboard
- **Learn** continuously through an MLOps feedback loop - confirmed fraud cases retrain and redeploy models with zero downtime
- **Explain** every decision via SHAP-based explainability reports, satisfying regulatory requirements (POPIA, PSD2, GDPR)
- **Audit** all decisions with tamper-evident logs for compliance and forensic investigation

---

## 📁 Repository Structure

```
SentinelPay/
├── README.md                       ← Project overview (you are here)
│
├──── Assignment 3 ──
├── SPECIFICATION.md                ← System specification
├── ARCHITECTURE.md                 ← C4 architectural diagrams - all 4 levels
│
├── ── Assignment 4 ──
├── STAKEHOLDER_ANALYSIS.md         ← 8-stakeholder analysis
├── SRD.md                          ← System Requirements Document - 15 FRs + 18 NFRs
├── REFLECTION.md                   ← Requirements engineering reflection
│
├── ── Assignment 5 ──
├── USE_CASE_DIAGRAM.md             ← UML use case diagram (Mermaid) - 7 actors, 14 use cases
├── USE_CASE_SPECIFICATIONS.md      ← 8 detailed use case specifications
├── TEST_CASES.md                   ← 10 functional test cases + 2 NFR test scenarios
├── REFLECTION_A5.md                ← Reflection on use case and test case development
│
├── ── Assignment 6 ──
├── AGILE_PLANNING.md               ← User stories, product backlog, sprint plan
├── REFLECTION_A6.md                ← Agile planning reflection
```

---

## 📄 Key Documents

### Assignment 3 - System Specification & Architecture

| Document | Description |
|---|---|
| [SPECIFICATION.md](./SPECIFICATION.md) | Full system specification - domain, problem statement, functional & non-functional requirements, use cases, and data models |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | C4 architectural diagrams - all 4 levels (Context, Container, Component, Code) with Mermaid diagrams and Architecture Decision Records |

### Assignment 4 - Stakeholder Analysis & Requirements Documentation

| Document | Description |
|---|---|
| [STAKEHOLDER_ANALYSIS.md](./STAKEHOLDER_ANALYSIS.md) | 8 stakeholders with detailed roles, key concerns, pain points, success metrics, influence levels, and conflict analysis |
| [SRD.md](./SRD.md) | System Requirements Document - 15 functional requirements with acceptance criteria + 18 non-functional requirements across 6 quality attribute categories |
| [REFLECTION.md](./REFLECTION.md) | Reflection on challenges faced in balancing stakeholder needs during requirements elicitation |

### Assignment 5 - Use Case Modeling and Test Case Development

| Document | Description |
|---|---|
| [USE_CASE_DIAGRAM.md](./USE_CASE_DIAGRAM.md) | UML use case diagram (Mermaid) with 7 actors, 14 use cases, and full written explanation of actors, relationships, and stakeholder alignment |
| [USE_CASE_SPECIFICATIONS.md](./USE_CASE_SPECIFICATIONS.md) | 8 detailed use case specifications with description, preconditions, postconditions, basic flow, and alternative flows |
| [TEST_CASES.md](./TEST_CASES.md) | 10 functional test cases + 2 NFR test scenarios (performance load test + security penetration test) in table format |
| [REFLECTION_A5.md](./REFLECTION_A5.md) | Reflection on challenges translating requirements to use cases and test cases |

### Assignment 6 - Agile Planning

| Document | Description |
|---|---|
| [AGILE_PLANNING.md](./AGILE_PLANNING.md) | 14 user stories, MoSCoW product backlog with Fibonacci story points, Sprint 1 plan with 27 tasks, and full traceability matrix |
| [REFLECTION_A6.md](./REFLECTION_A6.md) | Reflection on challenges in Agile prioritisation, estimation, and planning as a solo developer |
---

## 🧱 Technology Stack

| Layer | Technology |
|---|---|
| Event Streaming | Apache Kafka 3.x |
| ML Inference | Python 3.12 · XGBoost 2.x · HuggingFace Transformers · Isolation Forest |
| API Gateway | Kong Gateway 3.x |
| Backend Services | Java 21 (Spring Boot 3) · Python 3.12 (FastAPI) |
| Database | PostgreSQL 16 · Redis 7 · Apache Cassandra 4.x |
| MLOps | MLflow 2.x · Apache Airflow 2.x |
| Observability | Prometheus · Grafana · OpenTelemetry |
| Containerisation | Docker · Kubernetes (K8s) |
| CI/CD | GitHub Actions |

---

## Domain

**FinTech - Digital Payments & Financial Crime Prevention**

---

## 📊 Requirements At a Glance

| Category | Count |
|---|---|
| Stakeholders identified | 8 |
| Functional Requirements | 15 |
| Non-Functional Requirements | 18 (across 6 categories) |
| C4 Architecture Levels | 4 |
| Architecture Decision Records | 4 |

---

*SentinelPay - Because every millisecond between a transaction and a fraud signal costs money.*
