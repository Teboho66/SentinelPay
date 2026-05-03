# CHANGELOG

All notable changes to SentinelPay are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Assignment 10] – 2026-05-01

### Added

**Class Implementations (`/src`)**
- `src/models/enums.py` — Centralised enum types: `TransactionStatus`, `TransactionType`, `RiskLevel`, `AlertSeverity`, `NotificationChannel`, `PaymentMethodType`
- `src/models/transaction.py` — `Transaction` entity with private fields, `@property` getters, and business methods (`approve`, `block`, `set_risk_score`)
- `src/models/account.py` — `Account` entity with email validation, risk level management, and transaction linkage
- `src/models/domain.py` — Supporting entities: `FraudAlert`, `RiskScore`, `AuditLog`, `FraudRule`, `PaymentMethod` hierarchy (`CreditCard`, `DebitCard`, `DigitalWallet`), `Notification` hierarchy (`EmailNotification`, `SMSNotification`)

**Creational Patterns (`/creational_patterns`)**
- `simple_factory.py` — `TransactionFactory` with registry-based channel dispatch; concrete types: `OnlineTransaction`, `ATMTransaction`, `POSTransaction`, `WireTransferTransaction`
- `factory_method.py` — Abstract `AlertGenerator` with three concrete engines: `VelocityAlertGenerator`, `GeolocationAlertGenerator`, `MLAlertGenerator`
- `abstract_factory.py` — `NotificationFactory` interface with `EmailNotificationFactory` and `SMSNotificationFactory` product families; `AlertSummary` product hierarchy
- `builder.py` — `FraudCaseBuilder` with fluent API, required-field validation at `build()`, and auto-derived priority from `RiskScore`
- `prototype.py` — `FraudRuleCache` with five default prototypes; `FraudRule.clone()` via `copy.deepcopy`
- `singleton.py` — Thread-safe `AuditLogger` with double-checked locking, copy/deepcopy guards, and `_reset()` for test isolation

**Tests (`/tests`)**
- `test_simple_factory.py` — 16 tests covering all channels, case sensitivity, error paths, and sub-type metadata
- `test_factory_method.py` — 17 tests covering three generator types, threshold boundaries, severity mapping, and description content
- `test_abstract_factory.py` — 13 tests covering product types, send behaviour, summary rendering, and channel selector
- `test_builder.py` — 15 tests covering happy path, all three missing-field scenarios, escalation, priority derivation/override, audit trail accumulation, and type validation
- `test_prototype.py` — 13 tests covering default loading, clone identity, value equality, prototype immutability, unknown key handling, and custom rule registration
- `test_singleton.py` — 14 tests covering instance identity, direct-construction guard, log operations, filter, copy guards, thread safety (50 concurrent threads), and clear

**Documentation**
- `README_A10.md` — Language rationale, directory structure, class design decisions, pattern rationale with code examples, test instructions, and coverage summary
- `CHANGELOG.md` — This file

### Changed

- `Assignment 9/class_diagram.md` domain model translated to executable Python source code

### Fixed

- `Fix #12`: Thread-safe Singleton using double-checked locking with `threading.Lock`
- `Fix #13`: Prototype uses `copy.deepcopy` to ensure clone mutations cannot affect the canonical prototype
- `Fix #14`: Builder raises `ValueError` listing all missing required fields rather than raising on the first missing field only

---

## [Assignment 9] – 2026-04-15

### Added
- `domain_model.md` — 7-entity domain model with attributes, methods, and business rules
- `class_diagram.md` — Full Mermaid.js class diagram with UML relationships
- `a9_reflection.md` — Reflection on domain modelling and class diagram design

---

## [Assignment 8] – 2026-03-30

### Added
- `state_diagrams.md` — 8 UML state transition diagrams with explanations
- `activity_diagrams.md` — 8 UML activity diagrams with swimlanes
- `a8_reflection.md` — Reflection on state and activity modelling

---

## [Assignment 7] – 2026-03-15

### Added
- GitHub Kanban board configured for SentinelPay
- `template_analysis.md`, `kanban_explanation.md`, `reflection.md`

---

## [Assignment 6] – 2026-03-01

### Added
- `AGILE_PLANNING.md` — User stories, product backlog, sprint plan
- `REFLECTION_A6.md`

---

## [Assignment 5] – 2026-02-15

### Added
- `USE_CASE_DIAGRAM.md` — 7 actors, 14 use cases
- `USE_CASE_SPECIFICATIONS.md` — 8 detailed specifications
- `TEST_CASES.md` — 10 functional + 2 NFR test scenarios

---

## [Assignment 4] – 2026-02-01

### Added
- `STAKEHOLDER_ANALYSIS.md` — 8-stakeholder analysis
- `SRD.md` — 15 FRs + 18 NFRs
- `REFLECTION.md`

---

## [Assignment 3] – 2026-01-20

### Added
- `SPECIFICATION.md` — System specification
- `ARCHITECTURE.md` — C4 diagrams (all 4 levels)