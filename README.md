# 🛡️ SentinelPay - Real-Time Fraud Detection & Prevention Engine

[![CI/CD](https://github.com/Teboho66/SentinelPay/actions/workflows/ci.yml/badge.svg)](https://github.com/Teboho66/SentinelPay/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-288%20passing-brightgreen)](https://github.com/Teboho66/SentinelPay/actions)
[![Stars](https://img.shields.io/github/stars/Teboho66/SentinelPay?style=social)](https://github.com/Teboho66/SentinelPay/stargazers)
[![Forks](https://img.shields.io/github/forks/Teboho66/SentinelPay?style=social)](https://github.com/Teboho66/SentinelPay/network/members)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

> **Postgraduate Software Engineering**

> **Author:** Teboho Mokoni

> **Domain:** FinTech - Digital Payments & Financial Crime Prevention

> **Peer engagement:** ⭐ 28 stars · 🍴 36 forks · 4 merged external PRs
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


## 🚀 Quick Start

### Prerequisites

| Tool | Version |
|---|---|
| Python | 3.12+ |
| Git | 2.40+ |
| Docker (optional) | 24.0+ |

### Local Setup

```bash
# Clone
git clone https://github.com/Teboho66/SentinelPay.git
cd SentinelPay

# Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the API
cd "Assignment 12"
python run.py
```

**Swagger UI:** http://localhost:8000/docs
**Health check:** http://localhost:8000/health

### Docker

```bash
docker compose up
```

---

## 🧪 Running Tests

```bash
# Assignment 10 - Domain models + creational patterns (105 tests)
cd "Assignment 10"
PYTHONPATH="FraudRule:src:." pytest tests/ -v

# Assignment 11 - Repository layer (67 tests)
cd "Assignment 11"
PYTHONPATH="../Assignment 10:." pytest tests/ -v

# Assignment 12 - Service layer + REST API (116 tests)
cd "Assignment 12"
PYTHONPATH=".:../Assignment 10:../Assignment 11" pytest tests/ -v
```

**Total: 288 tests - 0 failures**

---

## 📡 API Reference

The full API is documented at `/docs` (Swagger UI) and `/redoc`.

### Transactions `/api/transactions`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/transactions` | Submit transaction for fraud evaluation |
| `GET` | `/api/transactions` | Get all transactions |
| `GET` | `/api/transactions/flagged` | Get all HARD_BLOCK transactions |
| `GET` | `/api/transactions/{id}` | Get transaction by ID |
| `POST` | `/api/transactions/{id}/decision` | Apply ML ensemble fraud decision |
| `DELETE` | `/api/transactions/{id}` | Delete transaction |

### Fraud Cases `/api/fraud-cases`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/fraud-cases` | Create investigation case (HIGH/CRITICAL only) |
| `GET` | `/api/fraud-cases` | Get all cases |
| `GET` | `/api/fraud-cases/queue` | Analyst queue sorted P1→P2→P3 |
| `GET` | `/api/fraud-cases/{id}` | Get case by ID |
| `PATCH` | `/api/fraud-cases/{id}/assign` | Assign to analyst |
| `PATCH` | `/api/fraud-cases/{id}/resolve` | Resolve CONFIRMED / DISMISSED |
| `DELETE` | `/api/fraud-cases/{id}` | Delete dismissed case |

### ML Models `/api/ml-models`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/ml-models` | Register new model version |
| `GET` | `/api/ml-models` | Get all models |
| `GET` | `/api/ml-models/production` | Get PRODUCTION models |
| `GET` | `/api/ml-models/{id}` | Get model by ID |
| `POST` | `/api/ml-models/{id}/evaluate` | Record evaluation metrics |
| `PATCH` | `/api/ml-models/{id}/promote` | Promote through lifecycle |
| `PATCH` | `/api/ml-models/{id}/hot-swap` | Reload artifact without restart |
| `DELETE` | `/api/ml-models/{id}` | Delete non-PRODUCTION model |

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, coding standards, and PR process.

1. Fork this repo
2. Pick a [`good-first-issue`](https://github.com/Teboho66/SentinelPay/issues?q=label%3Agood-first-issue)
3. Create a branch, make your change, write tests
4. Open a PR linking to the issue

See [ROADMAP.md](ROADMAP.md) for planned features across 7 phases.

## 📁 Repository Structure

```
SentinelPay/
│
├── ── Assignments 3–9 (Specification, Architecture, Planning, Modeling) ──
│
├── Assignment 3/               ← System specification + C4 architecture
├── Assignment 4/               ← Stakeholder analysis + SRD (15 FR + 18 NFR)
├── Assignment 5/               ← Use case modeling + test cases
├── Assignment 6/               ← Agile planning (14 stories, Sprint 1)
├── Assignment 7/               ← GitHub Kanban board
├── Assignment 8/               ← State + activity diagrams (8 each)
├── Assignment 9/               ← Domain model + Mermaid class diagram
│
├── ── Assignment 10 — Domain Code + Creational Patterns ──
│
├── Assignment 10/
│   ├── src/models/             ← Transaction, Account, FraudAlert, RiskScore,
│   │                              AuditLog, FraudRule, PaymentMethod, Notification
│   ├── FraudRule/
│   │   └── creational_patterns/← Simple Factory, Factory Method, Abstract Factory,
│   │                              Builder, Prototype, Singleton
│   └── tests/                  ← 105 tests
│
├── ── Assignment 11 — Repository Layer ──
│
├── Assignment 11/
│   ├── repositories/           ← Generic Repository[T,ID] + 7 entity interfaces
│   ├── repositories/inmemory/  ← HashMap implementations
│   ├── factories/              ← RepositoryFactory (MEMORY/FILESYSTEM/DATABASE)
│   ├── stubs/                  ← FileSystem + Database future backends
│   └── tests/                  ← 67 tests
│
├── ── Assignment 12 — Service Layer + REST API ──
│
├── Assignment 12/
│   ├── mapping/                ← TransactionService, FraudCaseService,
│   │                              MLModelService (business logic)
│   ├── handlers/routes/        ← FastAPI route handlers
│   ├── config/                 ← Pydantic schemas + dependency injection
│   ├── api/                    ← FastAPI app entry point
│   ├── repositories/           ← Local repo copies for A12
│   ├── services/exceptions.py  ← Domain exceptions → HTTP status codes
│   ├── docs/openapi.json       ← OpenAPI 3.1 spec
│   ├── run.py                  ← Server startup script
│   └── tests/                  ← 116 tests (service unit + API integration)
│
├── ── Assignment 13 — CI/CD Pipeline ──
│
├── .github/workflows/ci.yml    ← GitHub Actions: lint + 3 test jobs + wheel + Docker
├── Dockerfile                  ← Multi-stage Docker build
├── docker-compose.yml          ← Local stack with API
├── requirements.txt            ← Python dependencies
├── pyproject.toml              ← Package config + wheel build
├── Assignment 13/
│   ├── Protection.md           ← Branch protection rules + justification
│   └── docs/screenshots/       ← Branch protection, CI passing, PR blocked,
│                                  Swagger UI screenshots
│
├── ── Assignment 14 — Open-Source Readiness ──
│
├── CONTRIBUTING.md             ← Contributor guide (setup, standards, PR process)
├── ROADMAP.md                  ← 7 phases of planned features
├── LICENSE                     ← MIT License
├── VOTING_RESULTS.md           ← 28 ⭐ stars, 36 🍴 forks
├── Assignment 14/
│   ├── REFLECTION.md           ← 650-word reflection on open-source collaboration
│   └── docs/screenshots/       ← voting_results.png
│
├── ── Assignment 15 — Cross-Project Contributions ──
│
├── Assignment 15/
│   ├── CONTRIBUTIONS.md        ← Main submission file
│   ├── CONTRIBUTION_PLAN.md    ← Strategy + selected issues
│   ├── MERGED_PRS.md           ← 3 merged PRs across 4 repos
│   ├── REFLECTION.md           ← Collaboration lessons learned
│   └── docs/screenshots/
│       ├── first-peer-contribution/   ← TailorFit — PR merged ✅
│       ├── second-peer-contribution/  ← ClinicEase — PR opened
│       ├── third-peer-contribution/   ← Manga project — PR merged ✅
│       └── forth-peer-contribution/   ← CarWash — PR merged ✅
│
└── README.md                   ← This file
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
| [Domain_model.md](./Assignment%209/domain_model.md) | Domain model covering 7 core entities (Transaction, FraudCase, MLModel, AuditRecord, AccountProfile, CustomerDispute, StepUpChallenge) with attributes, methods, business rules, and entity relationships |
| [Class_diagram.md](./Assignment%209/class_diagram.md) | Full Mermaid.js UML class diagram with associations, aggregations, compositions, inheritance, and multiplicity across all domain entities |
| [A9_reflection.md](./Assignment%209/a9_reflection.md) | Reflection on abstraction challenges, class diagram alignment with prior assignments, trade-offs, and OO design lessons |

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

## ⚙️ CI/CD Pipeline

Every push to any branch triggers CI. Merging to `main` triggers CD.

```
Push to any branch
        │
        ▼
┌─────────────────────────────┐
│  CI  (runs on every branch) │
│  lint      → ruff checks    │
│  test-a10  → 105 tests      │
│  test-a11  → 67 tests       │
│  test-a12  → 116 tests      │
└─────────────────────────────┘
        │ merge to main only
        ▼
┌─────────────────────────────┐
│  CD  (main branch only)     │
│  build  → Python wheel      │
│  docker → GHCR image        │
│  release → GitHub Release   │
└─────────────────────────────┘
```

**Branch protection on `main`:**
- 1 approving review required
- All 4 CI status checks must be green
- Direct pushes blocked
- Linear history enforced

---

## 🌍 Open-Source Contributions (Assignment 15)

Contributions made to 4 classmate repositories:

| Project | Issue | PR | Status |
|---|---|---|---|
| TailorFit | good-first-issue #40 | Submitted | ✅ Merged |
| ClinicEase | Issue #13 | Submitted | 🔍 In Review |
| Manga Project | Issue #12 | Submitted | ✅ Merged |
| CarWash | Issue #76 | Submitted | ✅ Merged |

**3 out of 4 PRs merged.** Screenshots of each contribution are in `Assignment 15/docs/screenshots/`.

## 🧱 Technology Stack

| Layer | Technology |
|---|---|
| API Framework | Python 3.12 · FastAPI 0.115 |
| Data Validation | Pydantic 2.x |
| Testing | pytest · pytest-cov · httpx |
| Containerisation | Docker · Docker Compose |
| CI/CD | GitHub Actions |
| Container Registry | GitHub Container Registry (GHCR) |
| ML (planned) | XGBoost · Isolation Forest · DistilBERT |
| Streaming (planned) | Apache Kafka 3.x |
| Database (planned) | PostgreSQL 16 · Redis 7 · Cassandra |
| MLOps (planned) | MLflow · Apache Airflow |
| Observability (planned) | Prometheus · Grafana · OpenTelemetry |

## 🐳 Local Full-Stack Development with Docker

Run the SentinelPay FastAPI service together with PostgreSQL and Redis using Docker Compose from the repository root. The API currently uses in-memory repositories, but the local infrastructure is available for contributors working on database- and cache-backed features.

### Prerequisites

- Docker
- Docker Compose

### Start the full stack

```bash
docker compose up --build
```

Docker Compose starts these local services:

| Service | Host URL / Port | Purpose |
|---|---|---|
| API | <http://localhost:8000> | SentinelPay FastAPI application |
| PostgreSQL | `localhost:5432` | Local relational database |
| Redis | `localhost:6379` | Local cache / message broker dependency |

Default local connection settings are configured in `docker-compose.yml`:

| Variable | Value |
|---|---|
| `DATABASE_URL` | `postgresql://sentinelpay:sentinelpay@postgres:5432/sentinelpay` |
| `POSTGRES_DB` | `sentinelpay` |
| `POSTGRES_USER` | `sentinelpay` |
| `POSTGRES_PASSWORD` | `sentinelpay` |
| `POSTGRES_HOST` | `postgres` |
| `POSTGRES_PORT` | `5432` |
| `REDIS_URL` | `redis://redis:6379/0` |
| `REDIS_HOST` | `redis` |
| `REDIS_PORT` | `6379` |

The API waits for PostgreSQL and Redis health checks before starting. Once the stack is running, open:

- API health check: <http://localhost:8000/health>
- Swagger UI: <http://localhost:8000/docs>

To stop the stack and keep local data volumes:

```bash
docker compose down
```

To stop the stack and remove local PostgreSQL/Redis volumes:

```bash
docker compose down -v
```

## Project Stats

| Category | Count |
|---|---|
| Assignments completed | A3–A15 |
| Functional Requirements | 15 |
| Non-Functional Requirements | 18 |
| Domain entities | 7 |
| Creational patterns | 6 |
| REST API endpoints | 21 |
| Tests passing | 288 |
| CI/CD pipeline jobs | 8 |
| GitHub ⭐ Stars | 28 |
| GitHub 🍴 Forks | 36 |
| External PRs merged | 3 |

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

## 📄 Assignment Index

| # | Focus | Key Deliverable |
|---|---|---|
| A3 | System specification + C4 architecture | ARCHITECTURE.md |
| A4 | Stakeholder analysis + requirements | SRD.md — 15 FR + 18 NFR |
| A5 | Use case modeling + test cases | USE_CASE_SPECIFICATIONS.md |
| A6 | Agile planning | AGILE_PLANNING.md — 14 stories |
| A7 | GitHub Kanban board | Sprint Board — 7 columns |
| A8 | State + activity diagrams | 8 state + 8 activity diagrams |
| A9 | Domain model + class diagram | Class_diagram.md |
| A10 | Domain code + 6 creational patterns | 105 tests |
| A11 | Repository layer | 67 tests |
| A12 | Service layer + REST API | 21 endpoints · 116 tests |
| A13 | CI/CD pipeline + branch protection | ci.yml · Dockerfile |
| A14 | Open-source readiness | CONTRIBUTING.md · 28★ · 36🍴 |
| A15 | Cross-project contributions | 3 merged PRs |

---

*SentinelPay - Because every millisecond between a transaction and a fraud signal costs money.*
