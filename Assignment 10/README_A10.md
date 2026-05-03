# Assignment 10 – SentinelPay: From Class Diagrams to Code with All Creational Patterns

## Language Choice

**Python 3.12**

Python was chosen for the following reasons:

- SentinelPay's ML fraud-scoring layer (Assignment 3 architecture) is already defined as a Python microservice; implementing domain models in Python keeps the language consistent across the stack.
- Python's `abc` module, `dataclasses`, `copy`, and `threading` standard-library modules provide clean, idiomatic implementations of all six creational patterns without external dependencies.
- `pytest` and `pytest-cov` provide a mature test and coverage workflow with minimal configuration overhead, which is well-suited to an academic deliverable.

---

## Directory Structure

```
Assignment 10/
├── src/
│   └── models/
│       ├── enums.py          ← All shared Enum types
│       ├── transaction.py    ← Transaction entity
│       ├── account.py        ← Account entity
│       ├── domain.py         ← FraudAlert, RiskScore, AuditLog, FraudRule,
│       │                        PaymentMethod hierarchy, Notification hierarchy
│       └── __init__.py
│
├── creational_patterns/
│   ├── simple_factory.py     ← TransactionFactory
│   ├── factory_method.py     ← AlertGenerator hierarchy
│   ├── abstract_factory.py   ← NotificationFactory families
│   ├── builder.py            ← FraudCaseBuilder
│   ├── prototype.py          ← FraudRuleCache
│   ├── singleton.py          ← AuditLogger
│   └── __init__.py
│
├── tests/
│   ├── test_simple_factory.py
│   ├── test_factory_method.py
│   ├── test_abstract_factory.py
│   ├── test_builder.py
│   ├── test_prototype.py
│   ├── test_singleton.py
│   └── __init__.py
│
├── pytest.ini
├── README_A10.md             ← This file
└── CHANGELOG.md
```

---

## Class Implementations (`/src`)

Each class maps directly to an entity in the Assignment 9 Mermaid.js class diagram.

| Class | File | Key Design Decisions |
|---|---|---|
| `Transaction` | `transaction.py` | Private fields with `@property` getters. `set_risk_score()` automatically sets the `_flagged` flag when score ≥ 0.7. `update_status()` / `approve()` / `block()` provide named mutators. |
| `Account` | `account.py` | Email validated at construction. `transaction_ids` stored as a list of strings (foreign keys) rather than embedded objects to avoid circular dependencies. |
| `FraudAlert` | `domain.py` | Immutable after creation except for `resolve()`. `AlertSeverity` is an integer enum so severity values can be compared with `>`. |
| `RiskScore` | `domain.py` | Value object (no `id`). `risk_level()` derives a `RiskLevel` enum from the numeric score at query time. |
| `AuditLog` | `domain.py` | Fully immutable; no setters. Intended to be append-only. |
| `FraudRule` | `domain.py` | Implements `clone()` via `copy.deepcopy` for the Prototype pattern. Kept as a concrete class (no abstract base) so it can be instantiated directly when registering prototypes. |
| `PaymentMethod` | `domain.py` | Abstract base class with three concrete sub-types: `CreditCard`, `DebitCard`, `DigitalWallet`. Each implements `get_masked_identifier()` for PCI-DSS-safe display. |
| `Notification` | `domain.py` | Abstract base class. `send()` is abstract; each sub-type formats for its channel. `_sent` flag prevents double-dispatch errors. |

---

## Creational Pattern Implementations (`/creational_patterns`)

### 1. Simple Factory — `TransactionFactory`

**Rationale:** Transaction creation is triggered from multiple entry points: REST API controllers, Kafka consumers, and batch import jobs. Without centralisation, each call-site would need to know which concrete class to instantiate and how to populate channel-specific metadata. `TransactionFactory.create()` is a single, discoverable point of change.

**Pattern mechanics:** A static `_REGISTRY` dict maps channel strings to concrete classes. `create()` looks up the key and delegates construction.

```python
txn = TransactionFactory.create("ONLINE", 1500.00, "ZAR", "MER-001", "ACC-042")
```

---

### 2. Factory Method — `AlertGenerator`

**Rationale:** SentinelPay has three independent fraud-detection engines (velocity, geolocation, ML). Each engine knows how to decide *whether* to raise an alert and *how* to construct one. The `generate()` template method on the abstract `AlertGenerator` handles the detection workflow; `create_alert()` is the factory method delegated to each sub-class.

**Pattern mechanics:** `AlertGenerator` is abstract. `VelocityAlertGenerator`, `GeolocationAlertGenerator`, and `MLAlertGenerator` each implement `create_alert()` and `_should_alert()`. Adding a new engine requires only a new sub-class — the calling pipeline never changes.

```python
generator = MLAlertGenerator()
alert = generator.generate(transaction_id, risk_score=0.87)
```

---

### 3. Abstract Factory — `NotificationFactory`

**Rationale:** Each communication channel (Email, SMS) requires two related products: an alert notification and a case-summary report, both formatted consistently for that channel. Abstracting over the *family* ensures that an email alert is always paired with an email summary, not an SMS summary.

**Pattern mechanics:** `NotificationFactory` declares `create_notification()` and `create_summary()`. `EmailNotificationFactory` and `SMSNotificationFactory` implement both. The `dispatch()` convenience method creates and sends both products in one call.

```python
factory = get_notification_factory("EMAIL")
result = factory.dispatch(alert, recipient="analyst@sentinelpay.io")
```

---

### 4. Builder — `FraudCaseBuilder`

**Rationale:** `FraudCase` is an aggregate with seven fields, most of which are optional (audit trail, investigator notes, escalation flag). A direct constructor with that many parameters — especially optional ones — would be fragile and unreadable at call-sites. The fluent Builder makes intent explicit and validates at `build()` rather than silently accepting bad state.

**Pattern mechanics:** Each `with_*` method sets one field and returns `self` (fluent API). `build()` validates that all required fields are set and raises a descriptive `ValueError` listing what is missing. Priority is automatically derived from `RiskScore` but can be overridden with `set_priority()`.

```python
case = (
    FraudCaseBuilder("CASE-001")
    .with_transaction(txn)
    .with_alert(alert)
    .with_risk_score(score)
    .with_notes("Escalated per compliance policy")
    .escalate()
    .build()
)
```

---

### 5. Prototype — `FraudRuleCache`

**Rationale:** Fraud rules are initialised by parsing policy documents, loading thresholds from configuration stores, and calibrating against historical data — a non-trivial cost. `FraudRuleCache` loads each rule once as a canonical prototype. Per-merchant threshold customisation clones the base rule rather than re-initialising from scratch, keeping the canonical prototype untouched.

**Pattern mechanics:** `FraudRule.clone()` wraps `copy.deepcopy()`. `FraudRuleCache.get_clone()` fetches the prototype by ID and returns a deep copy. Consumers mutate their clone freely without side-effects on the cache.

```python
cache = FraudRuleCache()
cache.load_defaults()
merchant_rule = cache.get_clone("HIGH_VELOCITY")
merchant_rule.set_threshold(5)          # merchant-specific override
```

---

### 6. Singleton — `AuditLogger`

**Rationale:** Regulatory compliance requires a single, authoritative audit trail. Multiple instances would split entries across separate logs, creating gaps during a compliance audit. The Singleton also prevents duplicate entries that would arise if two logger instances both responded to the same event.

**Pattern mechanics:** Double-checked locking with `threading.Lock` ensures thread safety without acquiring the lock on every read after the first instantiation. `__copy__` and `__deepcopy__` are overridden to raise `RuntimeError`, preventing the Singleton from being accidentally cloned.

```python
logger = AuditLogger.get_instance()
logger.log("TRANSACTION_BLOCKED", actor="rule_engine", details={"rule": "LARGE_AMOUNT"})
```

---

## Running the Tests

```bash
# Install dependencies
pip install pytest pytest-cov

# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov=creational_patterns --cov-report=term-missing
```

### Test Coverage Summary

| Module | Coverage |
|---|---|
| `creational_patterns/abstract_factory.py` | 100% |
| `creational_patterns/factory_method.py` | 100% |
| `creational_patterns/prototype.py` | 100% |
| `creational_patterns/simple_factory.py` | 100% |
| `creational_patterns/builder.py` | 97% |
| `creational_patterns/singleton.py` | 92% |
| `src/models/enums.py` | 100% |
| `src/models/domain.py` | 80% |
| `src/models/transaction.py` | 78% |
| `src/models/account.py` | 52% |
| **Total** | **86%** |

The uncovered lines in `account.py` and `domain.py` are getters and `__repr__` methods on supporting entities not directly exercised by pattern-level tests. The pattern implementations themselves average 97%.

---

## GitHub Issues Linked

- `Fix #10: Implement all six creational patterns`
- `Fix #11: Add unit tests for all patterns`
- `Fix #12: Thread-safe Singleton implementation`
- `Fix #13: Deep-copy Prototype to prevent prototype mutation`
- `Fix #14: Builder validates required fields at build() time`