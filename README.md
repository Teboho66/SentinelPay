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
│
├── Assignment 7/
│   ├── template_analysis.md            ← GitHub template comparison and justification
│   ├── kanban_explanation.md           ← Kanban board definition and purpose
│   ├── reflection.md                   ← Lessons learned from Kanban implementation
│   └── screenshots/                    ← Board screenshots (kanban_board_full.png, issue_detail.png)
│
├── Assignment 8/
│   ├── state_diagrams.md               <- 8 UML state transition diagrams with explanations
│   ├── activity_diagrams.md            <- 8 UML activity diagrams with swimlanes
│   └── a8_reflection.md               <- Reflection on state and activity modeling
│
├── Assignment 9/
│   ├── domain_model.md                 <- Domain model - 7 entities with attributes, methods, business rules
│   ├── class_diagram.md                <- Full Mermaid.js class diagram with UML relationships
│   └── a9_reflection.md               <- Reflection on domain modeling and class diagram design
│
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

### Assignment 7 - GitHub Kanban Board

| Document | Description |
|---|---|
| [template_analysis.md](./Assignment%207/template_analysis.md) | Comparison of 4 GitHub project templates, justification for selecting Automated Kanban, and 7-column customisation plan |
| [kanban_explanation.md](./Assignment%207/kanban_explanation.md) | Kanban board definition, workflow visualisation, WIP limits, and Agile principles alignment |
| [reflection.md](./Assignment%207/reflection.md) | Lessons learned - GitHub Projects vs Trello vs Jira, WIP limit enforcement gaps, template customisation challenges |

### Assignment 8 - State and Activity Modeling

| Document | Description |
|---|---|
| [state_diagrams.md](./Assignment%208/state_diagrams.md) | 8 UML state transition diagrams (Transaction, Fraud Case, ML Model Version, Customer Dispute, Audit Record, Step-Up Auth, Account Profile, Kafka Offset) with guard conditions and FR mapping |
| [activity_diagrams.md](./Assignment%208/activity_diagrams.md) | 8 UML activity diagrams with swimlanes, decision nodes, and parallel actions (ingestion, scoring, decision, step-up auth, case review, model retraining, dispute, audit report) |
| [a8_reflection.md](./Assignment%208/a8_reflection.md) | Reflection on granularity decisions, aligning diagrams with Agile stories, and state vs activity diagram comparison |

### Assignment 9 - Domain Model and Class Diagram

| Document | Description |
|---|---|
| [domain_model.md](./Assignment%209/domain_model.md) | Domain model covering 7 core entities (Transaction, FraudCase, MLModel, AuditRecord, AccountProfile, CustomerDispute, StepUpChallenge) with attributes, methods, business rules, and entity relationships |
| [class_diagram.md](./Assignment%209/class_diagram.md) | Full Mermaid.js UML class diagram with associations, aggregations, compositions, inheritance, and multiplicity across all domain entities |
| [a9_reflection.md](./Assignment%209/a9_reflection.md) | Reflection on abstraction challenges, class diagram alignment with prior assignments, trade-offs, and OO design lessons |

---

## 🗂️ GitHub Project Board

The SentinelPay Sprint Board is managed using GitHub Projects with a customised Automated Kanban template.

**Board:** [SentinelPay Sprint Board](https://github.com/Teboho66/SentinelPay/projects)

### Board Customisation

The default Automated Kanban template was extended with 4 additional columns to match the SentinelPay development workflow:

| Column | Purpose | WIP Limit |
|---|---|---|
| Sprint 2 Backlog | Should-have and Could-have stories deferred from Sprint 1 | None |
| Sprint 1 - To Do | Must-have stories committed for Sprint 1 delivery | None |
| In Progress | Actively being developed | Max 2 |
| Testing | Implementation complete, test cases being executed | Max 2 |
| Blocked | Cannot proceed - dependency or blocker identified | None |
| In Review | Complete, under final self-review | Max 1 |
| Done | Meets Definition of Done from AGILE_PLANNING.md | None |

**Why Automated Kanban:** GitHub's automation rules (auto-move on issue open, close, reopen, PR merge) keep the board accurate without manual updates - critical for a solo developer managing 27 sprint tasks across 14 user stories.

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


## Project Stats

| Category | Count |
|---|---|
| Stakeholders identified | 8 |
| Functional Requirements | 15 |
| Non-Functional Requirements | 18 (across 6 categories) |
| C4 Architecture Levels | 4 |
| Use Cases | 14 |
| Use Case Specifications | 8 |
| Test Cases | 12 (10 functional + 2 NFR) |
| User Stories | 14 |
| Sprint 1 Tasks | 27 |
| Kanban Board Columns | 7 |
| State Transition Diagrams | 8 |
| Activity Diagrams | 8 |
| Domain Entities | 7 |

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
