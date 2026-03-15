# 🛡️ SentinelPay - Real-Time Fraud Detection & Prevention Engine

> **Postgraduate Software Engineering - Assignment 3**
> **Author:** Teboho Mokoni

---

## What is SentinelPay?

SentinelPay is an intelligent, real-time fraud detection and prevention engine designed for modern financial institutions and FinTech platforms. It combines streaming transaction processing, machine learning inference, behavioural analytics, and automated response orchestration to identify and neutralise fraudulent activity **before it causes financial damage** - at sub-100ms latency, at scale.

In 2026, card-not-present fraud, identity spoofing, and AI-generated synthetic identity attacks are the dominant threat vectors in digital payments. SentinelPay is architected specifically to combat these threats using an event-driven microservices backbone, ensemble ML models (gradient boosting + transformer-based anomaly detection), and a feedback loop that continuously retrains on confirmed fraud signals.

### What SentinelPay Will Do Once Completed

- **Ingest** live transaction streams from payment processors, mobile wallets, and banking APIs via Kafka event pipelines
- **Score** every transaction in real time using a multi-model ML ensemble (XGBoost + Isolation Forest + fine-tuned BERT for merchant text signals)
- **Enforce** automated rule-based and ML-driven decisions: approve, flag for review, or block — with configurable thresholds per customer risk tier
- **Alert** customers and fraud analysts instantly via push notification, SMS, and a case management dashboard
- **Learn** continuously through an MLOps feedback loop - confirmed fraud cases retrain and redeploy models with zero downtime
- **Explain** every decision via SHAP-based explainability reports, satisfying regulatory requirements (POPIA, PSD2, GDPR)
- **Audit** all decisions with tamper-evident logs for compliance and forensic investigation

---

## 📁 Repository Structure

```
SentinelPay/
├── README.md               ← You are here
├── SPECIFICATION.md        ← Full system specification
├── ARCHITECTURE.md         ← C4 architectural diagrams (all 4 levels)

```

---

## 📄 Key Documents

| Document | Description |
|---|---|
| [SPECIFICATION.md](./SPECIFICATION.md) | Full system specification - domain, problem statement, functional & non-functional requirements, use cases, and data models |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | C4 architectural diagrams - Context, Container, Component, and Code levels with full Mermaid diagrams |

---

## 🧱 Technology Stack (Proposed)

| Layer | Technology |
|---|---|
| Event Streaming | Apache Kafka |
| ML Inference | Python · XGBoost · HuggingFace Transformers |
| API Gateway | Kong Gateway |
| Backend Services | Java 21 (Spring Boot 3) · Python 3.12 (FastAPI) |
| Database | PostgreSQL · Redis · Apache Cassandra |
| MLOps | MLflow · Apache Airflow |
| Observability | Prometheus · Grafana · OpenTelemetry |
| Containerisation | Docker · Kubernetes (K8s) |
| CI/CD | GitHub Actions |

---

## 🎯 Domain

**FinTech - Digital Payments & Financial Crime Prevention**

---

*SentinelPay - Because every millisecond between a transaction and a fraud signal costs money.*