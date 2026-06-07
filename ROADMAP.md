# SentinelPay Roadmap

This roadmap outlines the planned features and improvements for SentinelPay.
Items marked ✅ are complete. Items marked 🔨 are in progress. Items marked 📋 are planned.

---

## ✅ Completed (Assignments 9–13)

| Feature | Assignment |
|---|---|
| Domain model — 7 entities, 5 value objects, 9 enums | A9 |
| All six creational design patterns | A10 |
| Repository layer with in-memory + factory pattern | A11 |
| TransactionService, FraudCaseService, MLModelService | A12 |
| REST API — 21 endpoints with OpenAPI docs | A12 |
| GitHub Actions CI/CD pipeline | A13 |
| Docker multi-stage build + GHCR publish | A13 |
| Branch protection + PR workflow | A13 |

---

## 📋 Phase 2 — Database Persistence

**Goal:** Replace the in-memory HashMap store with real databases.

| Feature | Label | Complexity |
|---|---|---|
| PostgreSQL repository for Transaction + AuditRecord | `good-first-issue` | Medium |
| Redis repository for AccountProfile velocity counters | `feature-request` | Medium |
| Apache Cassandra for 30-day amount baseline storage | `feature-request` | Hard |
| Database migration scripts (Alembic) | `good-first-issue` | Easy |
| Docker Compose with PostgreSQL + Redis services | `good-first-issue` | Easy |

---

## 📋 Phase 3 — ML Scoring Integration

**Goal:** Connect the API to real ML models.

| Feature | Label | Complexity |
|---|---|---|
| XGBoost model training script on IEEE-CIS dataset | `feature-request` | Hard |
| Isolation Forest anomaly scorer | `feature-request` | Medium |
| MLflow model registry integration | `feature-request` | Hard |
| Feature vector validation (Pydantic schema versioning) | `good-first-issue` | Easy |
| SHAP explainability endpoint for fraud cases | `feature-request` | Hard |

---

## 📋 Phase 4 — Kafka Event Streaming

**Goal:** Make SentinelPay event-driven as designed in the A3 architecture.

| Feature | Label | Complexity |
|---|---|---|
| Kafka producer in Transaction submission endpoint | `feature-request` | Hard |
| Kafka consumer for fraud decision events | `feature-request` | Hard |
| Dead-letter queue for failed schema validation | `good-first-issue` | Medium |
| Docker Compose Kafka + Zookeeper setup | `good-first-issue` | Easy |

---

## 📋 Phase 5 — Step-Up Authentication

**Goal:** Implement OTP challenge for SOFT_DECLINE transactions.

| Feature | Label | Complexity |
|---|---|---|
| StepUpChallenge REST endpoints | `good-first-issue` | Medium |
| OTP generation + Redis TTL enforcement | `feature-request` | Medium |
| Twilio SMS integration (test mode) | `feature-request` | Medium |
| OTP validation with attempt counting | `good-first-issue` | Easy |

---

## 📋 Phase 6 — Observability

**Goal:** Make the system production-observable.

| Feature | Label | Complexity |
|---|---|---|
| Prometheus metrics endpoint (`/metrics`) | `good-first-issue` | Easy |
| Grafana dashboard for P50/P95/P99 latency | `feature-request` | Medium |
| Structured JSON logging (structlog) | `good-first-issue` | Easy |
| OpenTelemetry distributed tracing | `feature-request` | Hard |

---

## 📋 Phase 7 — Customer Dispute Portal

**Goal:** Let customers dispute HARD_BLOCK transactions via the API.

| Feature | Label | Complexity |
|---|---|---|
| CustomerDisputeService | `good-first-issue` | Medium |
| Dispute REST endpoints | `good-first-issue` | Medium |
| 30-day dispute window enforcement (BR-CD3) | `good-first-issue` | Easy |
| 48-hour SLA tracker | `feature-request` | Medium |

---

## 💡 How to Contribute

Pick any **`good-first-issue`** item from the tables above. They are designed
to be self-contained and well-scoped for new contributors.

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and PR instructions.

---

*Last updated: May 2026 | SentinelPay — Teboho Mokoni*

