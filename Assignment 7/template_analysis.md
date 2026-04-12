# template_analysis.md - GitHub Project Template Analysis and Selection
## SentinelPay: Real-Time Fraud Detection & Prevention Engine

> **Assignment 7 - Template Analysis**
> Builds on Assignment 6 Sprint Plan (AGILE_PLANNING.md)

## 1. Overview

GitHub Projects offers several pre-built templates designed to support different team workflows and project management styles. This document evaluates four of GitHub's available project templates against the specific needs of SentinelPay, selects the most appropriate one, and justifies that selection with reference to the Sprint 1 plan defined in Assignment 6.

---

## 2. Template Comparison Table

| Feature | Basic Kanban | Automated Kanban | Bug Triage | Team Planning |
|---|---|---|---|---|
| **Default Columns** | To Do, In Progress, Done | To Do, In Progress, Done | Needs Triage, High Priority, Low Priority, Closed | To Do, In Progress, Done, Backlog |
| **Number of Default Columns** | 3 | 3 | 4 | 4 |
| **Automation - Issue Opened** | None | Auto-moves to To Do | Auto-moves to Needs Triage | None |
| **Automation - PR Merged** | None | Auto-moves to Done | Auto-moves to Closed | None |
| **Automation - Issue Closed** | None | Auto-moves to Done | Auto-moves to Closed | None |
| **Automation - Issue Reopened** | None | Auto-moves back to In Progress | Auto-moves back to Needs Triage | None |
| **WIP Limiting Support** | Manual only | Manual only | Manual only | Manual only |
| **Sprint Planning Support** | Not built-in | Not built-in | Not applicable | Basic backlog column |
| **Best Suited For** | Small teams, simple workflows, learning Kanban basics | Teams using GitHub Issues heavily, wanting reduced manual board management | Teams tracking software defects and bugs with severity triage | Teams planning work across multiple people with a backlog |
| **Agile Methodology Alignment** | Low - no automation, no sprint structure | High - automation reduces admin overhead, keeps board current without manual moves | Low - focused on bugs, not feature delivery | Medium - backlog column supports sprint planning but lacks automation |
| **Customisability** | High - simple base to build on | High - automation rules are editable | Medium - triage workflow is opinionated | High - backlog structure is flexible |
| **Suitable for SentinelPay** | Partially - too simple for a multi-stage ML pipeline | Yes - automation aligns with Kafka-driven, event-based development workflow | No - SentinelPay is feature development, not primarily bug tracking | Partially - backlog is useful but lacks automation |

---

## 3. Template Descriptions

### 3.1 Basic Kanban
The Basic Kanban template provides three columns: To Do, In Progress, and Done. It has no automation - all card movements between columns are manual. It is the simplest starting point and is well-suited for teams new to Kanban or projects with straightforward linear workflows. For SentinelPay, Basic Kanban is insufficient because the pipeline has distinct stages (development, testing, review, blocked) that a three-column board cannot represent clearly.

### 3.2 Automated Kanban
The Automated Kanban template starts with the same three columns as Basic Kanban but adds GitHub automation rules: when an issue is opened it moves to To Do automatically, when a pull request is merged or an issue is closed it moves to Done, and when an issue is reopened it moves back to In Progress. This reduces the manual overhead of keeping the board current. For SentinelPay, where each user story is tracked as a GitHub Issue (set up in Assignment 6), this automation means the board stays accurate as issues are opened, worked on, and closed without requiring the developer to manually drag cards.

### 3.3 Bug Triage
The Bug Triage template is designed specifically for defect management workflows. Its columns (Needs Triage, High Priority, Low Priority, Closed) reflect a severity-based sorting process rather than a development progress flow. While SentinelPay will produce bugs during development, the primary workflow at this stage is feature delivery from the Sprint 1 backlog - not bug triage. This template is not appropriate as the primary project management tool for SentinelPay at this stage.

### 3.4 Team Planning
The Team Planning template adds a Backlog column to the standard three-column layout, which is useful for distinguishing between work planned for a future sprint and work actively in progress. However, it lacks the automation of the Automated Kanban template, meaning all card movements are manual. For a solo developer managing 27 sprint tasks, the manual overhead is a real productivity cost.

---

## 4. Selected Template: Automated Kanban

**Template Selected:** Automated Kanban

### 4.1 Justification

The Automated Kanban template is the most appropriate choice for SentinelPay for the following reasons:

**Reason 1 - Automation aligns with the GitHub Issues setup from Assignment 6**
In Assignment 6, all 14 user stories were created as GitHub Issues with labels, milestones, and assignments. The Automated Kanban template is designed specifically to work with GitHub Issues - when an issue is opened it appears on the board automatically, and when it is closed it moves to Done without any manual intervention. This means the board reflects the true state of development at all times, not just when the developer remembers to update it manually.

**Reason 2 - Supports Sprint 1 structure from AGILE_PLANNING.md**
The Sprint 1 plan in Assignment 6 selected 6 user stories (US-001, US-002, US-003, US-004, US-006, US-011) comprising 33 story points and 27 tasks. The Automated Kanban board will be customised with additional columns (Sprint 1 - To Do, Testing, Blocked, Sprint 2 Backlog) to reflect this sprint structure precisely - something neither Basic Kanban nor Team Planning supports out of the box.

**Reason 3 - Reduced admin overhead for a solo developer**
SentinelPay is a solo project. Every minute spent manually updating a project board is a minute not spent on development. The automation rules in Automated Kanban (auto-move on issue open, close, merge, reopen) keep the board current with zero manual effort, which is directly relevant to the solo developer context described in AGILE_PLANNING.md.

**Reason 4 - Extensibility**
The Automated Kanban template provides a clean three-column base that is easy to extend with custom columns. This document defines the customisation plan in detail, and the template's simplicity makes adding Testing, Blocked, and In Review columns straightforward without disrupting the existing automation rules.

---

## 5. Customisation Plan

The base Automated Kanban template will be customised as follows to match the SentinelPay Sprint 1 workflow:

| Column Name | Purpose | WIP Limit | Automation |
|---|---|---|---|
| **Sprint 2 Backlog** | Should-have and Could-have stories not in Sprint 1 | None | Manual |
| **Sprint 1 - To Do** | Must-have stories selected for Sprint 1 | None | Issues assigned to Sprint 1 milestone auto-added |
| **In Progress** | Story currently being actively developed | 2 tasks max | Auto-moved when issue assigned |
| **Testing** | Story implementation complete, test cases from TEST_CASES.md being executed | 2 tasks max | Manual move |
| **Blocked** | Story cannot proceed due to a dependency or unresolved issue | None | Manual move |
| **In Review** | Story complete and under self-review before closing | 1 task max | Manual move |
| **Done** | Story meets Definition of Done from AGILE_PLANNING.md | None | Auto-moved when issue closed |

**WIP Limit Rationale:** The In Progress column is limited to 2 tasks maximum. This is a deliberate constraint based on the Kanban principle that limiting work-in-progress reduces context switching and increases the probability of completing tasks rather than accumulating partially-done work. For a solo developer this is especially important - having more than 2 stories simultaneously in progress is a reliable predictor of none of them being finished by the sprint end. The Testing column is also limited to 2 to prevent a backlog of untested stories building up at the end of the sprint.
