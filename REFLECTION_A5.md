# REFLECTION_A5.md - Reflection on Use Case Modeling and Test Case Development
## SentinelPay: Real-Time Fraud Detection & Prevention Engine

> **Assignment 5 - Reflection**
> Author: Teboho Mokoni 

---

Going into this assignment I thought translating requirements into use cases would be the straightforward part - I already had 15 functional requirements from Assignment 4 with acceptance criteria, so surely the use cases just follow from those. That assumption was wrong pretty quickly.

The first challenge I hit was figuring out the right level of abstraction for the use case diagram. My first draft had 20+ use cases and it was a mess - I had things like "Validate JWT Token" and "Query Redis Cache" as use cases, which are implementation details, not user interactions. A use case should describe what an actor wants to achieve, not how the system does it internally. Once I reframed every use case as a goal an actor is trying to accomplish - "Submit Transaction Dispute," "Review and Resolve Fraud Case" - the diagram cleaned up significantly. The key learning there is that use cases live at the user goal level, not the system mechanism level.

The second challenge was the include and extend relationships. I initially had them backwards for a few cases. I had "Complete Step-Up Authentication" as an include of "Enforce Fraud Decision," which implies step-up auth always happens on every decision - it doesn't. It only happens on SOFT_DECLINE. That's an extend, not an include. Getting this distinction right matters because include means "always happens" and extend means "conditionally happens under specific circumstances." Once I mapped each relationship to its actual business condition, the diagram became accurate and the written explanation became much easier to justify with reference to the FR that drives each relationship.

The test case development was where I found the biggest gap between what I assumed would be easy and what was actually difficult. Writing a test case that genuinely validates a requirement - not just exercises the happy path - requires thinking about what can go wrong. For TC-002 (missing mandatory field), TC-005 (blacklist pre-filter blocking ML scoring), and the SQL injection sub-test in NFR-Test-002, I had to think adversarially about the system rather than optimistically. That shift in thinking - from "does this work when everything is fine" to "does this fail safely when things go wrong" - is what separates a useful test suite from a superficial one.

The NFR performance test was also more involved than I expected. Specifying that the latency test needs a 5-minute warm-up phase before the actual measurement period, and that OpenTelemetry trace spans are the measurement mechanism rather than just a stopwatch at the HTTP layer, required understanding the actual measurement challenge. End-to-end latency in an event-driven system spans multiple Kafka publish and consume operations - you cannot measure it from a single service's perspective.

Overall what this assignment made clear is that requirements, use cases, and test cases form a chain where each level is only as strong as the one before it. The quality of the use case specifications depended entirely on the specificity of the Assignment 4 requirements. And the test cases are only meaningful if the use case specifications have clear preconditions and postconditions to test against. The chain either holds end-to-end or it breaks - there is no partial credit from the system's perspective.

---
