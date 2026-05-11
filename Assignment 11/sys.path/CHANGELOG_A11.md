# CHANGELOG – Assignment 11

## [Assignment 11] – 2026-05-10

### Added

**Repository Interfaces (`/repositories`)**
- `base.py` — Generic `Repository[T, ID]` ABC with `save()`, `find_by_id()`, `find_all()`, `delete()`, `count()`, `exists()`
- `interfaces.py` — 7 entity-specific interfaces: `TransactionRepository`, `FraudCaseRepository`, `MLModelRepository`, `AuditRecordRepository`, `AccountProfileRepository`, `CustomerDisputeRepository`, `StepUpChallengeRepository` — each with domain-specific query methods traced to SRD functional requirements

**In-Memory Implementations (`/repositories/inmemory`)**
- `base_inmemory.py` — `InMemoryRepository[T]` base with dict storage, `threading.Lock` thread safety, `_get_id()` hook pattern
- `implementations.py` — 7 concrete implementations; each overrides `_get_id()` explicitly; `InMemoryAuditRecordRepository.delete()` raises `RuntimeError` (BR-AR2); `find_tampered()` implements NFR-S4 daily integrity scan; `find_expired()` implements StepUpChallenge TTL cleanup

**Factory (`/factories`)**
- `repository_factory.py` — `RepositoryFactory.get(entity, storage_type)` resolves MEMORY/FILESYSTEM/DATABASE backends; case-insensitive entity and storage type lookup; 7 typed convenience helpers (e.g., `get_transaction_repo()`)

**Stubs (`/stubs`)**
- `filesystem_repository.py` — JSON file-backed stub using `to_kafka_payload()` / `to_compliance_report()` serialisers; thread-safe writes; demonstrates future filesystem backend
- `database_repository.py` — PostgreSQL/MongoDB stub documenting exact SQL/NoSQL queries per CRUD method; raises `NotImplementedError` to prevent silent data loss

**Tests (`/tests`)**
- `test_repositories.py` — 52 tests covering CRUD and domain queries across all 7 repositories; includes `find_tampered()` positive and negative cases; `find_expired()` with TTL=0; `delete()` raises `RuntimeError` on AuditRecord
- `test_factory.py` — 15 tests covering all 7 entity resolutions, case-insensitivity, unknown entity/storage type errors, new instance per call, all typed helpers, filesystem and database stub resolution

### Fixed

- `Fix #22` — `AuditRecord.verify_integrity()` (in Assignment 10 `entities.py`) was calling `compute_hash()` which overwrites `_record_hash`, causing it to always return `True` even for tampered records. Fixed by computing the HMAC inline without mutating state.

### Notes for push

Files to add to the SentinelPay repo:
```
Assignment 11/
├── repositories/
├── factories/
├── stubs/
├── tests/
├── conftest.py
├── pytest.ini
├── README_A11.md
└── CHANGELOG_A11.md
```

Also update `Assignment 10/src/models/entities.py` with the `verify_integrity()` fix.

GitHub issues to create before pushing:
- `#16` through `#22` as listed in README_A11.md