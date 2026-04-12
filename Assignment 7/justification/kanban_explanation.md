# kanban_explanation.md - Kanban Board Definition and Purpose
## SentinelPay: Real-Time Fraud Detection & Prevention Engine


## 1. What is a Kanban Board?

A Kanban board is a visual project management tool that represents the state of all active work in a system at a single glance. The word "Kanban" comes from Japanese, meaning "visual signal" or "card" - it originated in Toyota's manufacturing system in the 1940s as a way to control production flow and eliminate waste. In software development, the same principle applies: work items (tasks, user stories, bugs) are represented as cards that move across columns from left to right, where each column represents a stage in the development workflow.

The defining characteristics of a Kanban board are:

- **Columns represent workflow stages** - not time periods or people, but the state a piece of work is in
- **Cards represent individual work items** - in SentinelPay's case, each card is a GitHub Issue representing a user story or task
- **WIP limits prevent overload** - each column can have a maximum number of cards, forcing the team to finish work before starting new work
- **Flow is continuous** - unlike Scrum which has fixed-length sprints, Kanban tracks the continuous movement of work from creation to completion

For SentinelPay specifically, the Kanban board at `https://github.com/Teboho66/SentinelPay` in the Projects tab is the single source of truth for what is being worked on, what is blocked, and what is done at any point in the Sprint 1 delivery cycle.


## 2. How the SentinelPay Kanban Board Works

### 2.1 Visualising Workflow

The SentinelPay board uses seven columns to represent the complete lifecycle of a user story from the backlog to completion:

```
Sprint 2 Backlog → Sprint 1 - To Do → In Progress → Testing → Blocked → In Review → Done
```

Each column answers a specific question:

| Column | Question Answered | Cards Currently Here |
|---|---|---|
| **Sprint 2 Backlog** | What is planned but not yet started in this sprint? | US-007, US-008, US-009, US-010, US-012, US-013, US-014 |
| **Sprint 1 - To Do** | What has been committed to Sprint 1 but not started? | US-001, US-002, US-003, US-004, US-006, US-011 |
| **In Progress** | What is being actively worked on right now? | Max 2 cards (WIP limit enforced) |
| **Testing** | What has been implemented and is being validated against TEST_CASES.md? | Max 2 cards (WIP limit enforced) |
| **Blocked** | What cannot proceed due to a dependency, missing information, or technical blocker? | No limit - visibility is the goal |
| **In Review** | What is complete and undergoing final self-review before closing? | Max 1 card |
| **Done** | What fully meets the Definition of Done from AGILE_PLANNING.md? | Auto-populated when issues are closed |

This column structure directly maps to the SentinelPay development process. The Testing column is particularly important because each user story has specific test cases defined in TEST_CASES.md (Assignment 5) - a story cannot move to Done without those tests passing. Having a dedicated Testing column makes this gate visible on the board rather than hiding it inside the "In Progress" state.

The Blocked column surfaces problems that are often invisible in simpler three-column boards. In an event-driven microservices architecture like SentinelPay, a service often cannot be tested until an upstream service (e.g., the Ingestion Service) is working. If US-004 (ML Scoring) is blocked because the Kafka enriched topic is not yet producing events, that blocker needs to be visible on the board so it can be resolved before the sprint burns down.

### 2.2 Limiting Work-in-Progress (WIP)

The SentinelPay board enforces WIP limits on three columns:

- **In Progress: maximum 2 cards**
- **Testing: maximum 2 cards**
- **In Review: maximum 1 card**

WIP limits are the most important and most frequently ignored element of Kanban. The reason for the limit is mathematical: in a system where one person is working on 5 things simultaneously, each thing gets 20% of their attention. In a system where that same person works on 2 things, each gets 50% of their attention and both are far more likely to be completed before new work is started.

For SentinelPay's Sprint 1, the WIP limit of 2 in the In Progress column means that if US-001 and US-002 are both in progress and US-003 needs to start, either US-001 or US-002 must be moved to Testing first. This creates a natural forcing function - the developer must finish and test work before picking up new work, which is exactly the behaviour that prevents the common sprint failure pattern of having everything 80% done at sprint end.

The specific limit of 2 (not 1, not 3) is chosen because SentinelPay's architecture has some natural parallelism: for example, writing a test case for US-001 while implementing US-002 is genuinely parallel work. But more than 2 active items for a solo developer creates context-switching overhead that outweighs the parallelism benefit.

### 2.3 Supporting Agile Principles

The SentinelPay Kanban board supports the following Agile principles from the Agile Manifesto:

**Continuous delivery of working software**
The board's flow from To Do through Testing to Done ensures that only tested, verified stories are marked as complete. Every card that reaches Done represents a working piece of the SentinelPay pipeline - not just written code, but code that has passed the acceptance criteria defined in AGILE_PLANNING.md. The Testing column enforces this by making test execution a visible, mandatory stage rather than an afterthought.

**Responding to change**
The Blocked column enables rapid response to unexpected technical obstacles. When a card is moved to Blocked, the immediate question becomes: what needs to happen to unblock it? In SentinelPay's context, this might mean discovering that Cassandra takes longer than expected to initialise before feature data is available for US-004. Making the blocker visible on the board means it gets resolved faster than if it were buried in a task description.

**Simplicity - maximising the amount of work not done**
The WIP limits enforce a form of simplicity - by preventing the start of new work before existing work is finished, the board pushes toward completing fewer things fully rather than starting many things partially. For the SentinelPay MVP definition (a working end-to-end fraud detection pipeline), a partially-implemented scoring service and a partially-implemented audit service together are worth zero. A fully implemented and tested ingestion service is worth something concrete.

**Sustainable pace**
The board provides visibility into the real state of work. Unlike a status report that can be optimistic, the Kanban board shows exactly how many cards are in each stage. If six cards are stuck in Testing with the sprint ending in two days, that is visible immediately and action can be taken - deprioritise two stories, move them back to Sprint 2 Backlog, and focus on getting four done properly. This kind of real-time adjustment is only possible when workflow is visualised honestly.

## 3. Board Labels Used

The following GitHub Issue labels are used on cards in the SentinelPay board to provide additional context at a glance:

| Label | Colour | Meaning |
|---|---|---|
| `user-story` | Blue | The card represents a full user story from AGILE_PLANNING.md |
| `must-have` | Red | MoSCoW Must-have priority |
| `should-have` | Orange | MoSCoW Should-have priority |
| `could-have` | Yellow | MoSCoW Could-have priority |
| `sprint-1` | Green | Selected for Sprint 1 delivery |
| `nfr` | Purple | Non-functional requirement story |
| `blocked` | Dark red | Currently blocked - needs attention |


## 4. Kanban vs Scrum for SentinelPay

Although Assignment 6 used Scrum concepts (sprint, sprint goal, story points, Definition of Done), the board implementation uses Kanban. This is a deliberate and valid combination - many real-world teams use a hybrid approach called "Scrumban" where Scrum's planning cadence structures the work and Kanban's visual board manages the daily flow.

For SentinelPay specifically, the Kanban board is more appropriate than a pure Scrum board because:
- A solo developer does not need the ceremony of daily standups or sprint retrospectives
- The continuous flow visibility of Kanban is more informative than a simple burndown chart for a single-person project
- The WIP limits enforce discipline without requiring a Scrum Master to enforce it socially

The Scrum elements (sprint goal, user stories, Definition of Done) from Assignment 6 are preserved and visible in the board structure - Sprint 1 stories are in a dedicated column, and the Done column requires the Definition of Done to be met. The Kanban board is the implementation layer on top of the Scrum planning layer.
