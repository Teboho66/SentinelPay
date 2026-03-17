# REFLECTION.md - Challenges in Balancing Stakeholder Needs
## SentinelPay: Real-Time Fraud Detection & Prevention Engine

> **Assignment 4 - Requirements Engineering Reflection**
> Author: Teboho Nkosi | March 2026

---

## Introduction

Requirements engineering is rarely a purely technical exercise. For SentinelPay, the process of eliciting, analysing, and documenting requirements from eight distinct stakeholders surfaced a set of genuine tensions that no single requirement could fully resolve. This reflection documents the three most significant challenges encountered in balancing those competing needs, the trade-off reasoning applied, and what I would approach differently in a professional context.

---

## Challenge 1: The False Positive Paradox - Customer Experience vs. Fraud Detection Effectiveness

The most persistent tension in the SentinelPay requirements was between the Bank Customer's need for frictionless payment approvals and the combined pressure from the Compliance Officer, Financial Regulator, and Executive Leadership to maximise fraud catch rates.

From the bank customer's perspective, a blocked legitimate transaction is not a minor inconvenience - it is an embarrassing, trust-destroying failure that happens at the worst possible moment (a supermarket till, an international hotel check-in, a medical payment). The customer doesn't see a fraud detection system at work; they see a bank that doesn't trust them. Customer churn data from the industry consistently shows that customers who experience two or more false declines in a year are significantly more likely to switch institutions. This means false positives are not just a usability problem - they are a direct revenue and retention problem that the CFO cares about deeply.

On the other side, the Compliance Officer and the Financial Regulator need the system to catch as much fraud as possible. Every confirmed fraud case that slips through becomes potential regulatory exposure and direct financial loss. There is no "acceptable" fraud rate from a compliance perspective.

The challenge is that these two objectives are mathematically in tension. In any binary classification system, increasing sensitivity (catching more fraud) inherently decreases specificity (at the cost of more false positives), and vice versa. You cannot simultaneously maximise both metrics with a single threshold.

**How I resolved this in the requirements:** Rather than writing a single detection threshold, I designed the system with per-account-tier and per-channel configurable thresholds (FR-07, FR-06). High-value business accounts can have lower false positive tolerance. High-risk channels (international card-not-present) can have higher sensitivity. The SOFT_DECLINE decision tier (FR-08) creates a middle ground - suspicious transactions are not blindly blocked but challenged with step-up authentication, allowing legitimate customers to self-identify. This preserves both customer experience (legitimate customers get through, with minimal friction) and security (genuine fraud cannot complete the step-up challenge).

**What I would do differently:** In a real engagement, I would run a formal decision analysis workshop with the CFO and CCO together, presenting the precision-recall trade-off curve and asking them to agree on an operating point. The threshold is ultimately a business decision, not a technical one, and documenting that decision with explicit sign-off from both stakeholders is critical for accountability.

---

## Challenge 2: Latency vs. Explainability - The Regulatory Compliance Tension

The second major conflict was between the Payment Processor Integration Team's strict latency requirement (P99 ≤ 100ms end-to-end) and the Compliance Officer's requirement that every HARD_BLOCK decision must be accompanied by a SHAP explainability report.

SHAP computation - specifically `TreeExplainer` for the XGBoost model and `KernelExplainer` for the Isolation Forest - is computationally expensive. A full SHAP explanation for a single transaction can take 200–800ms depending on model complexity and the number of features. This is 2–8× the entire allowed latency budget for the fraud decision itself. Satisfying both requirements simultaneously with a naive synchronous implementation is physically impossible.

Initially I modelled this as a hard constraint that would require architectural compromise - either accept higher latency (breaking the payment processor's SLA) or skip SHAP for some decisions (breaking the compliance officer's requirement). Neither option was acceptable.

**How I resolved this in the requirements:** The solution was to recognise that the compliance officer's requirement is about the *availability* of an explanation, not its *synchronous delivery with the decision*. A regulator or analyst does not need the SHAP report in the same 100ms window - they need it to exist and be retrievable when they review a case, which may be hours or days later. By making SHAP computation asynchronous - the decision is returned in real time, and the SHAP report is computed in a background job and stored in object storage within 30 seconds - both requirements are satisfied without compromise (FR-15, NFR-P1). The `shap_report_ref` field in the audit record points to the stored report.

This was a good example of resolving an apparent conflict by questioning the implicit assumption - the assumption that "must have a SHAP report" means "must have it synchronously." Surfacing and challenging that assumption with the compliance stakeholder changed the requirements without changing either party's actual business need.

**What I would do differently:** I should have validated the asynchronous SHAP approach explicitly with the Compliance Officer in a requirements review session before finalising the SRD. In a real project, a stakeholder can accept a proposed resolution in principle but raise new concerns when they see the implementation - for example, a regulator might require SHAP reports to be generated within a defined SLA (e.g., 5 minutes) rather than accepting an unbounded async delay. Getting that constraint on paper early would have strengthened the requirement.

---

## Challenge 3: Innovation Velocity vs. Operational Stability - The ML Engineer and Payment Processor Conflict

The third significant tension was between the ML Engineer's need for rapid iteration on model improvements and the Payment Processor Integration Team's need for a stable, predictable integration contract.

The ML Engineer's perspective is legitimate: fraud patterns evolve rapidly. A model that is 85% accurate today may be 70% accurate in three months as fraudsters adapt. The ability to retrain and redeploy models quickly - potentially multiple times per week - is not a nice-to-have; it is fundamental to the system's long-term effectiveness. Any friction in the deployment process directly translates to a degraded detection rate.

The Payment Processor Integration Team's perspective is equally legitimate: they have their own downstream systems, SLAs, and integration test suites that depend on SentinelPay's API contract. If the transaction event schema or decision response format changes unexpectedly, their systems break. In a real FinTech environment, a breaking API change can trigger contractual penalties and require emergency incident responses on both sides.

The initial conflict appeared to be between "change frequently" and "never change." But analysing the requirements more carefully revealed that the conflict was based on a false coupling. The ML model changes are entirely internal to SentinelPay - they affect the values of `fraud_score` and `risk_tier` but not the schema of the API request or response. The Payment Processor does not care whether the fraud score is produced by XGBoost version 2.1 or version 3.0 - they care that the response always contains a `decision` field with a valid enum value.

**How I resolved this in the requirements:** I explicitly separated the concerns. NFR-M1 (API documentation and versioning) guarantees API contract stability with a 30-day deprecation window for any breaking changes. FR-14 (zero-downtime model hot-swap) enables the ML Engineer to deploy new model versions at any time without any API change or service restart. The payment processor's integration never sees or cares about the model version - it is an internal implementation detail. This was a case where the apparent conflict dissolved entirely once the abstraction boundary was correctly identified.

**What I would do differently:** This conflict would have been identified and resolved faster if I had conducted a joint stakeholder workshop bringing the ML Engineer and the Payment Processor Integration Team into the same room (or call) to map the system boundary together. Each had a mental model of "what they were integrating with" that included implicit assumptions about what would and wouldn't change. Making those assumptions explicit early would have prevented the apparent conflict from ever forming.

---

## Broader Reflection: What Requirements Engineering Taught Me About SentinelPay

Working through this structured requirements elicitation process revealed aspects of SentinelPay's design that I had not fully considered in the architectural phase. Specifically:

**The human side of fraud detection.** The Assignment 3 architecture is a technically elegant distributed system, but Assignment 4 made it clear that the Fraud Analyst is not just a user - they are a critical component of the system's accuracy. Their ability to quickly and confidently resolve cases, and the quality of the feedback labels they provide, directly drives model performance. This means the Analyst Dashboard UX (NFR-U1, NFR-U2) is not a cosmetic concern but a system performance concern. A confusing interface reduces the quality of analyst decisions, which degrades the model, which increases analyst workload. The feedback loop is real.

**Regulatory requirements are architectural constraints, not afterthoughts.** The Compliance Officer and Regulator's requirements (PII tokenisation, tamper-evident audit logs, SHAP explainability, 7-year retention) are not features that can be bolted on later. They require architectural decisions made at the ingestion boundary, in the data model, and in the asynchronous processing design. Treating them as first-class requirements from day one - as this assignment forced me to do - produces a fundamentally different and more robust architecture than treating them as a compliance checklist.

**Stakeholder conflict is information.** Every conflict identified in the stakeholder analysis pointed to an architectural decision that needed to be made explicitly. The false positive paradox → configurable per-tier thresholds. The latency vs. explainability conflict → asynchronous SHAP generation. The stability vs. velocity conflict → clean API/model abstraction boundary. A system with no stakeholder conflicts either has no stakeholders or has not done the analysis properly.

---

## Theoretical Grounding

The approach taken in this assignment was informed by established requirements engineering theory and practice. This section connects the practical decisions made above to the academic frameworks they drew from.

**Sommerville's Stakeholder Classification Framework**
Ian Sommerville's *Software Engineering* (10th ed., 2016) distinguishes between system stakeholders at three levels: those who directly use the system (end users), those who manage or are responsible for it (organisational stakeholders), and those who have indirect interests such as regulatory bodies (external stakeholders). This three-tier classification directly shaped how the eight SentinelPay stakeholders were organised in STAKEHOLDER_ANALYSIS.md - Bank Customer and Fraud Analyst as primary users, Compliance Officer and ML Engineer as organisational stakeholders, and the Financial Regulator as the external institutional stakeholder. Sommerville also emphasises that stakeholder conflicts are a natural product of the elicitation process and must be managed rather than suppressed - a principle that drove the Stakeholder Conflict Analysis table.

**Wiegers and Beatty's Requirements Elicitation Principles**
Karl Wiegers and Joy Beatty's *Software Requirements* (3rd ed., 2013) establish that requirements must be: complete (nothing missing), consistent (no contradictions), verifiable (testable acceptance criteria), and traceable (linked to their origin). These four properties were used as the quality gate for every requirement written in the SRD. The decision to include explicit measurable acceptance criteria for every functional requirement - rather than writing requirements as abstract capability statements - was directly informed by Wiegers' principle that a requirement without an acceptance criterion is untestable and therefore unverifiable.

**The Volere Requirements Specification Template**
The Robertson and Robertson *Volere Requirements Specification Template* (Atlantic Systems Guild, 2012) introduced the concept of the "fit criterion" - a measurable condition that, when satisfied, confirms the requirement has been met. The "Acceptance Criteria" and "Measurement Criteria" sections in every SRD requirement are a direct application of the Volere fit criterion concept, ensuring that every stated requirement can be objectively verified rather than subjectively judged.

**IEEE Std 29148-2018 - Systems and Software Engineering: Life Cycle Processes - Requirements Engineering**
The IEEE 29148 standard formalises requirements engineering processes for systems and software. It specifies that non-functional requirements must be categorised by quality characteristic (performance, security, reliability, usability, maintainability, portability) and that each must include measurable thresholds. The six NFR categories used in the SRD (Usability, Deployability, Maintainability, Scalability, Security, Performance) align with this standard's quality characteristic taxonomy, adapted for a cloud-native microservices context.

**Conflict Resolution in RE: The Viewpoints Framework**
The Viewpoints framework (Finkelstein et al., 1992; later formalised by Nuseibeh, Kramer & Finkelstein, 1994) argues that stakeholder conflicts in requirements engineering arise because different stakeholders hold different "viewpoints" - partial, potentially inconsistent descriptions of the system from their own perspective. The framework recommends surfacing inter-viewpoint inconsistencies explicitly and resolving them through negotiation rather than ignoring them. The three conflicts documented in this reflection - false positive paradox, latency vs. explainability, and stability vs. velocity - were identified by applying exactly this approach: mapping each stakeholder's viewpoint, finding where they intersected inconsistently, and then reasoning through a resolution.

---

## References

Sommerville, I. (2016). *Software Engineering* (10th ed.). Pearson Education.
Wiegers, K. & Beatty, J. (2013). *Software Requirements* (3rd ed.). Microsoft Press.
Robertson, S. & Robertson, J. (2012). *Mastering the Requirements Process: Getting Requirements Right* (3rd ed.). Addison-Wesley.
IEEE Std 29148-2018. (2018). *Systems and Software Engineering - Life Cycle Processes - Requirements Engineering*. IEEE.
Nuseibeh, B., Kramer, J. & Finkelstein, A. (1994). A framework for expressing the relationships between multiple views in requirements specification. *IEEE Transactions on Software Engineering*, 20(10), 760-773.
Finkelstein, A., Gabbay, D., Hunter, A., Kramer, J. & Nuseibeh, B. (1994). Inconsistency handling in multiperspective specifications. *IEEE Transactions on Software Engineering*, 20(8), 569-578.

---

*SentinelPay REFLECTION.md - Version 2.0 | 23 March 2026*
*Assignment 4 - Requirements Engineering Reflection*