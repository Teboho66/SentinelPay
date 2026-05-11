# Assignment 11 – SentinelPay: Persistence Repository Layer

## Overview

This assignment implements a full repository layer for SentinelPay, persisting all
seven domain entities defined in the Assignment 9 class diagram. The layer abstracts
storage details behind interfaces, making it trivial to swap the in-memory HashMap
backend (used in tests and local dev) for PostgreSQL, Redis, MongoDB, or a JSON
filesystem store without changing any service-layer code.

---

## Directory Structure

```
Assignment 11/
├── repositories/
│   ├── base.py                 ← Generic Repository[T, ID] interface (6 methods)
│   ├── interfaces.py           ← 7 entity-specific interfaces with domain query methods
│   └── inmemory/
│       ├── base_inmemory.py    ← Shared HashMap + threading.Lock base class
│       └── implementations.py ← 7 concrete in-memory implementations
│
├── factories/
│   └── repository_factory.py  ← RepositoryFactory — storage-abstraction mechanism
│
├── stubs/
│   ├── filesystem_repository.py ← JSON file-backed stub (future backend)
│   └── database_repository.py  ← PostgreSQL/MongoDB stub (future backend)
│
├── tests/
│   ├── test_repositories.py    ← CRUD + domain query tests for all 7 repositories
│   └── test_factory.py         ← Factory resolution and error-path tests
│
├── conftest.py                 ← Adds Assignment 10 src to sys.path
├── pytest.ini
├── README_A11.md               ← This file
└── CHANGELOG_A11.md
```

---

## 1. Repository Interface Design

### Generic Interface (`repositories/base.py`)

```python
class Repository(ABC, Generic[T, ID]):
    def save(self, entity: T) -> None: ...       # Create / Update (upsert)
    def find_by_id(self, entity_id: ID) -> Optional[T]: ...
    def find_all(self) -> List[T]: ...
    def delete(self, entity_id: ID) -> None: ...
    def count(self) -> int: ...
    def exists(self, entity_id: ID) -> bool: ...
```

**Justification for generics:** Without `Generic[T, ID]`, each of the seven entity
repositories would duplicate the same six method signatures. Generics eliminate that
duplication while keeping each repository strongly typed — `TransactionRepository`
accepts and returns `Transaction` objects, not arbitrary dicts.

### Entity-Specific Interfaces (`repositories/interfaces.py`)

Each interface extends `Repository[EntityType, str]` and adds domain-specific query
methods. Every query method maps to a use case or functional requirement from prior
assignments:

| Repository | Domain Query Methods | Traced to |
|---|---|---|
| `TransactionRepository` | `find_by_account_id_token()`, `find_by_decision()`, `find_by_risk_tier()`, `find_flagged()` | FR-05, FR-07, UC11 |
| `FraudCaseRepository` | `find_by_transaction_id()`, `find_by_status()`, `find_by_priority()`, `find_open_cases()`, `find_by_analyst_id()` | FR-09, FR-10, UC8 |
| `MLModelRepository` | `find_by_model_name()`, `find_by_stage()`, `find_production_models()`, `find_by_name_and_stage()` | FR-13, FR-14 |
| `AuditRecordRepository` | `find_by_transaction_id()`, `find_by_decision()`, `find_tampered()` | FR-15, NFR-S4 |
| `AccountProfileRepository` | `find_new_accounts()`, `find_by_risk_tier_override()` | FR-05, BR-AP1 |
| `CustomerDisputeRepository` | `find_by_transaction_id()`, `find_by_status()`, `find_open_disputes()`, `find_by_customer_id_token()` | FR-12, UC7 |
| `StepUpChallengeRepository` | `find_by_transaction_id()`, `find_by_status()`, `find_expired()` | FR-08, UC5 |

---

## 2. In-Memory Implementation

### Base Class (`repositories/inmemory/base_inmemory.py`)

`InMemoryRepository[T]` provides the shared `dict`-backed storage and implements all
six generic CRUD methods. A `threading.Lock` guards every read and write to handle
concurrent Kafka consumer threads safely. Sub-classes inherit all CRUD and only
implement their entity-specific query methods.

Each concrete repository overrides `_get_id()` to extract its specific primary key
(`transaction_id`, `case_id`, `model_id`, `audit_id`, `account_id_token`,
`dispute_id`, `challenge_id`).

### Notable domain invariants enforced in implementations

- **`InMemoryAuditRecordRepository.delete()`** raises `RuntimeError` with a message
  citing BR-AR2 — matching the production PostgreSQL role restriction that revokes
  DELETE privilege on the `audit_records` table. Audit records can never be deleted.

- **`InMemoryAuditRecordRepository.find_tampered()`** re-runs `verify_integrity()`
  against every stored record using the HMAC signing key, returning only those that
  fail. This implements the NFR-S4 daily tamper-detection scan.

- **`InMemoryStepUpChallengeRepository.find_expired()`** calls `is_expired()` on
  every GENERATED or DELIVERED challenge to find those whose 120-second TTL has
  elapsed. In production this is Redis TTL enforcement; in-memory it is a Python
  timestamp comparison.

---

## 3. Storage-Abstraction Mechanism

### Why Factory over Dependency Injection?

Both patterns are valid. The choice here is **Factory** for these reasons:

SentinelPay already uses DI at the microservice level (Spring Boot `@Autowired`,
FastAPI `Depends`). At the Python repository layer in this academic project, a
Factory is a better fit because:

1. **Environment switching is a single string argument.** Changing from `"MEMORY"` to
   `"DATABASE"` in one place switches every repository in the service — no DI
   container configuration to update.
2. **No DI framework dependency.** A plain `RepositoryFactory.get()` call works
   identically in pytest, in a FastAPI route, and in a standalone script.
3. **Explicit.** A junior developer reading the service code immediately sees which
   storage backend is in use. DI containers can obscure this behind annotation
   scanning and autowiring.

### Usage

```python
# In a service class — decoupled from storage implementation
from factories import RepositoryFactory

txn_repo = RepositoryFactory.get("Transaction", "MEMORY")     # tests / local dev
txn_repo = RepositoryFactory.get("Transaction", "DATABASE")   # production (stub)
txn_repo = RepositoryFactory.get("Transaction", "FILESYSTEM") # audit archival

txn_repo.save(transaction)
case = txn_repo.find_by_id("TXN-001")
blocked = txn_repo.find_flagged()
```

Typed convenience methods are also available for IDE autocomplete:

```python
txn_repo  = RepositoryFactory.get_transaction_repo()
case_repo = RepositoryFactory.get_fraud_case_repo()
ml_repo   = RepositoryFactory.get_ml_model_repo()
```

---

## 4. Future-Proofing

### FileSystem JSON Backend (`stubs/filesystem_repository.py`)

Demonstrates serialisation to `/tmp/sentinelpay/<entity>.json`. Uses
`to_kafka_payload()` (Transaction) or `to_compliance_report()` (AuditRecord) for
serialisation, with a generic `__dict__` fallback. Thread-safe file writes via
`threading.Lock`. A full implementation would add entity-specific JSON-to-domain-
object deserialisation.

**When this would be used:**
- Local development without a running database
- Audit log archival to flat files for long-term retention (BR-AR3: 7 years)
- Regulatory JSON export for the Compliance Officer (UC11)

### Database Backend (`stubs/database_repository.py`)

Shows the connection setup pattern for PostgreSQL (SQLAlchemy) and MongoDB
(PyMongo). Each CRUD method stub documents the exact SQL/NoSQL query it would
execute. Raises `NotImplementedError` to make it immediately obvious when a
production database connection is missing — not silently losing data.

**SentinelPay production mapping (from A3 ARCHITECTURE.md):**

| Entity | Production Store |
|---|---|
| Transaction, FraudCase, AuditRecord, CustomerDispute | PostgreSQL |
| AccountProfile | Redis (primary) + Cassandra (30-day baseline) |
| MLModel | MLflow Model Registry (PostgreSQL backend) |
| StepUpChallenge | Redis with TTL enforcement |

### Updated Class Diagram

```
Repository[T, ID]  ←── (extends) ── TransactionRepository
     ↑                              FraudCaseRepository
     │                              MLModelRepository
InMemoryRepository[T]               AuditRecordRepository
     ↑                              AccountProfileRepository
     ├── InMemoryTransactionRepository      CustomerDisputeRepository
     ├── InMemoryFraudCaseRepository        StepUpChallengeRepository
     ├── InMemoryMLModelRepository
     ├── InMemoryAuditRecordRepository   FileSystemRepositoryStub
     ├── InMemoryAccountProfileRepository DatabaseRepositoryStub
     ├── InMemoryCustomerDisputeRepository
     └── InMemoryStepUpChallengeRepository

RepositoryFactory ──get("Transaction","MEMORY")──→ InMemoryTransactionRepository
                  ──get("Transaction","FILESYSTEM")→ FileSystemRepositoryStub
                  ──get("Transaction","DATABASE")──→ DatabaseRepositoryStub
```

---

## Running the Tests

```bash
# From Assignment 11 root
pip install pytest pytest-cov
pytest tests/ -v
pytest tests/ --cov=repositories --cov=factories --cov=stubs --cov-report=term-missing
```

### Test Coverage

| Module | Coverage |
|---|---|
| `factories/repository_factory.py` | 98% |
| `repositories/base.py` | 100% |
| `repositories/interfaces.py` | 98% |
| `repositories/inmemory/base_inmemory.py` | 81% |
| `repositories/inmemory/implementations.py` | 94% |
| `stubs/filesystem_repository.py` | 43% |
| `stubs/database_repository.py` | 67% |
| **Total** | **86%** |

Lower stub coverage is expected — stubs raise `NotImplementedError` by design for
unimplemented methods; exercising those paths would require a live database or
filesystem write, which belongs in integration tests not unit tests.

---

## GitHub Issues

- `Fix #16: Define generic Repository[T,ID] interface with 6 CRUD methods`
- `Fix #17: Implement 7 entity-specific repository interfaces with domain queries`
- `Fix #18: In-memory HashMap implementations for all 7 repositories`
- `Fix #19: AuditRecord delete() raises RuntimeError (BR-AR2 enforcement)`
- `Fix #20: RepositoryFactory with MEMORY/FILESYSTEM/DATABASE backends`
- `Fix #21: FileSystem and Database repository stubs for future-proofing`
- `Fix #22: Fix AuditRecord.verify_integrity() mutation bug (always returned True)`