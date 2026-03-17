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
├── README.md                   ← Project overview (you are here)
├── SPECIFICATION.md            ← System specification (Assignment 3)
├── ARCHITECTURE.md             ← C4 architectural diagrams - all 4 levels (Assignment 3)
├── STAKEHOLDER_ANALYSIS.md     ← 8-stakeholder analysis with roles, concerns, pain points, metrics (Assignment 4)
├── SRD.md                      ← System Requirements Document - 15 FRs + 18 NFRs (Assignment 4)
└── REFLECTION.md               ← Requirements engineering reflection (Assignment 4)
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

## 🎯 Domain

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