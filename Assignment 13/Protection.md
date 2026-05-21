# Branch Protection Rules – SentinelPay

## Overview

SentinelPay processes real-time fraud decisions for financial transactions.
A bug reaching the `main` branch does not just break a website — it can
either let fraudulent transactions through or block legitimate ones.
Both outcomes cause direct financial harm.

Branch protection rules are the last line of defence between a developer
error and a production incident.

---

## Rules Applied to `main`

### 1. Require Pull Request Reviews (at least 1 approving review)

**Why:** A second pair of eyes catches logic errors that automated tests miss.
A fraud scoring bug might pass all tests but produce incorrect risk tiers for
a specific account tier — something a reviewer would notice when reading the
diff. In a financial system, unreviewed code reaching production is a
compliance risk under POPIA and FSCA regulations.

**Configured:** Require 1 approving review before merge.
Dismiss stale reviews when new commits are pushed — so approving an old
version and then sneaking in a change does not bypass the rule.

---

### 2. Require Status Checks to Pass Before Merging

**Why:** The CI pipeline runs 288 tests across three assignments (A10: 105,
A11: 67, A12: 116). If any test fails — including the AuditRecord
tamper-detection test, the BR-ML1 promotion gate, or the BR-FC2 note
enforcement — the PR cannot be merged. This guarantees that the business
rules defined in the SRD are always enforced in the codebase.

**Required status checks:**
- `Lint (ruff)` — style and syntax
- `Test A10 — Domain Models & Creational Patterns`
- `Test A11 — Repository Layer`
- `Test A12 — Service Layer & REST API`

All four must be green before merge is permitted.

---

### 3. Require Branches to Be Up to Date Before Merging

**Why:** A PR that was approved and green yesterday might conflict with a
change merged today. Requiring the branch to be up to date forces the
developer to rebase or merge `main` into their branch and re-run CI before
the merge button becomes active. This prevents the "it worked on my branch"
class of production incidents.

---

### 4. Disable Direct Pushes to `main`

**Why:** Developers pushing directly to `main` bypass code review, bypass
CI testing, and bypass the audit trail that PRs provide. In regulated
financial systems, every change to production code must be traceable to a
reviewed, approved request. Direct pushes make incident investigation much
harder — there is no PR description, no review thread, and no linked issue.

SentinelPay's audit trail (FR-15, AuditRecord) applies to transaction
decisions; the same principle of tamper-evident, reviewable history applies
to the codebase itself.

---

### 5. Restrict Who Can Dismiss Pull Request Reviews

**Why:** If a reviewer raises a concern and requests changes, only the
repository administrator should be able to dismiss that review — not the
author of the PR. This prevents a developer from dismissing a blocking
review and merging anyway.

---

### 6. Require Linear History (No Merge Commits)

**Why:** Merge commits create a non-linear git history that is hard to read
and hard to bisect when hunting for the commit that introduced a bug.
Requiring squash merges or rebases keeps `git log --oneline` on `main`
readable and makes `git bisect` effective for incident response.

---

## How These Rules Interact with the CI/CD Pipeline

```
Developer pushes feature branch
        ↓
CI runs automatically (lint + 3 test jobs)
        ↓
Developer opens PR to main
        ↓
CI runs again on the PR (required status checks)
        ↓
    ┌───────────────────────────────┐
    │  All 4 status checks green?   │
    │  At least 1 approving review? │
    │  Branch up to date with main? │
    └───────────────────────────────┘
           ↓ YES             ↓ NO
      Merge allowed     Merge blocked
           ↓
    CD pipeline runs:
      - Python wheel built
      - Docker image pushed to GHCR
      - GitHub Release created (on tags)
```

---

## Setting Up These Rules in GitHub

1. Go to **Settings → Branches → Branch protection rules**
2. Click **Add rule**
3. Branch name pattern: `main`
4. Enable:
   - [x] Require a pull request before merging
     - [x] Require approvals: **1**
     - [x] Dismiss stale pull request approvals when new commits are pushed
   - [x] Require status checks to pass before merging
     - [x] Require branches to be up to date before merging
     - Add status checks: `Lint (ruff)`, `Test A10`, `Test A11`, `Test A12`
   - [x] Require linear history
   - [x] Do not allow bypassing the above settings
5. Click **Save changes**

---

*SentinelPay PROTECTION.md — Assignment 13*
*Author: Teboho Mokoni | CPUT Postgraduate Diploma in Software Engineering*