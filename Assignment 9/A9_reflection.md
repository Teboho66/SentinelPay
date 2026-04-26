# a9_reflection.md - Reflection on Domain Modeling and Class Diagram Design
## SentinelPay: Real-Time Fraud Detection & Prevention Engine

> **Assignment 9 - Reflection**
> Author: Teboho Mokoni

## Challenges in Designing the Domain Model and Class Diagram

The hardest part of this assignment was not drawing the diagram - it was deciding what belongs in the domain model at all. SentinelPay has a large surface area: Kafka topics, Redis caches, MLflow registries, PostgreSQL tables, Python ML models, Java Spring Boot services. All of these are part of the system, but most of them are implementation details, not domain entities. The domain model is supposed to capture business concepts - things that a domain expert like a Compliance Officer or Fraud Analyst would recognise and discuss. A Kafka topic is not a domain concept. A FraudCase is.

The line between an entity and a service was the most difficult abstraction decision. My first draft had a KafkaConsumer class, a RedisClient class, and a MLflowClient class. These are technically accurate - the system uses all three - but they belong in the infrastructure layer, not the domain layer. The domain layer should be ignorable of infrastructure. Removing them forced me to ask: what does the domain actually care about? It cares about Transactions, FraudCases, MLModels, and AuditRecords. How those objects are persisted or transmitted is an infrastructure concern. This distinction - domain versus infrastructure - is central to Domain-Driven Design and it took real effort to apply consistently.

The relationship modelling was the second major challenge. Composition, aggregation, and association are easy to define abstractly but harder to distinguish in practice. For Transaction and FraudCase, the question was: can a FraudCase exist without its Transaction? The answer is no - a FraudCase without a Transaction has no meaning. That makes it composition. For EnsembleScorer and MLModel, the question was: do the MLModel instances have independent lifecycles? Yes - they are trained separately, versioned separately in MLflow, and can be individually replaced via hot-swap. That makes it aggregation, not composition. Getting these right required going back to the state diagrams from Assignment 8 and asking: when the Transaction is created, what else comes into existence? When the Transaction lifecycle ends, what else ends with it?

## Alignment with Prior Assignments

The class diagram is not an isolated artifact - every class, attribute, and method in it is traceable to something in a prior assignment.

The Transaction class attributes map directly to the JSON schema defined in Assignment 4 SRD.md (FR-02). The mandatory fields `transactionId`, `accountIdToken`, `merchantId`, `amount`, `currency`, `timestamp`, `channel`, `deviceFingerprintToken`, `ipAddressHash`, and `geolocation` are the exact fields listed in the schema validation requirement. The `amount: BigDecimal` type choice traces to the data model in Assignment 3 SPECIFICATION.md which notes that monetary values must use DECIMAL(19,4) to avoid floating point errors.

The MLModel class with its `precision`, `recall`, `meetsPromotionGate()`, and `hotSwap()` methods maps directly to FR-13 and FR-14 from the SRD. The `EvaluationMetrics.meetsPromotionGate()` method encodes Business Rule BR-ML1 (precision >= 0.85 AND recall >= 0.80) as a first-class method on a value object rather than buried in a service implementation. This makes the business rule visible at the class level - exactly what the domain model is for.

The AuditRecord class with `recordHash` and `verifyIntegrity()` maps to FR-15 and NFR-S4. The state diagram from Assignment 8 showed the AuditRecord transitioning from Writing to Persisted to Verified or Tampered - each of those states is now visible in the AuditRecord class as implicit states in the `recordHash` field (present after Write) and `verifyIntegrity()` method (the Verified/Tampered transition).

The StepUpChallenge class maps to UC5 from Assignment 5 (USE_CASE_SPECIFICATIONS.md). The alternative flows in UC5 - correct OTP, expired OTP, max attempts exceeded - are directly implemented in `validateOTP()`, `isExpired()`, and `escalateToHardBlock()` methods. The use case specification drove the method design.

## Trade-offs Made

The most significant trade-off was the decision to include service classes (EnsembleScorer, DecisionEngine, AuditService, MLOpsRetrainingPipeline) in the class diagram. Purist domain modeling would exclude them - a domain model should contain only entities and value objects, not services. But the assignment brief asks for a class diagram that shows the full system structure, and excluding these service classes would make the diagram incomplete as a system representation.

The second trade-off was granularity of the enumeration classes. I could have modelled RiskTier, FraudDecision, CaseStatus, and the others as simple string constants rather than explicit enumeration classes. Including them as full enum classes adds visual noise to the diagram but makes the domain model more precise - a reviewer knows immediately that RiskTier has exactly four valid values (LOW, MEDIUM, HIGH, CRITICAL), not an arbitrary string. For a FinTech system where invalid state values can cause incorrect fraud decisions, this precision is worth the visual cost.

## Lessons Learned About Object-Oriented Design

The most valuable insight from this assignment was how directly the Module 6 lecture concepts apply to real design decisions. The lecture covers McCabe's cyclomatic complexity (CC = E - N + 2P) and the Chidamber-Kemerer metrics (WMC, DIT, CBO, LCOM). Looking at the EnsembleScorer class through these lenses: it aggregates three models, has a direct dependency on CircuitBreaker, and uses FeatureVector and ModelScore as parameters. Its Coupling Between Objects (CBO) is around 4-5, which is within the acceptable threshold (CBO > 5 requires refactoring per the lecture). The fact that a class like DecisionEngine has low coupling - it only depends on DecisionThresholds and Transaction - is not accidental. It was designed that way to keep CBO low and maintainability high.

The ISO 25010 coding standards from Module 6 also influenced method design. Each method has a single responsibility, takes typed parameters rather than generic Maps, and returns typed results rather than void with side effects. The `validate()` method on Transaction and CustomerDispute returns Boolean (not void throwing exceptions) because the calling code needs to branch on the result - a testable, explicit contract rather than an implicit exception-based one. These are the kinds of decisions that separate code that meets functional requirements from code that is maintainable over time.

The domain model is ultimately a communication tool. Every decision in it - which entities exist, how they relate, what their multiplicities are - is a claim about the business domain that can be validated with a domain expert. The business rules table in domain_model.md is not documentation for documentation's sake. It is the contract between the class diagram and the functional requirements, making the system verifiable at the design level before a single line of code is written.
