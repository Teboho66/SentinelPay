# CONTRIBUTIONS.md - Assignment 15 Submission 🌍

**Author:** Teboho Mokoni
**Repository:** https://github.com/Teboho66/SentinelPay
**Assignment:** 15 - Cross-Project Contributions & Collaborative Development

---

## Quick Links

| Deliverable             | File                                           | Status                |
| ----------------------- | ---------------------------------------------- | --------------------- |
| Contribution Plan       | [CONTRIBUTION_PLAN.md](./CONTRIBUTION_PLAN.md) | ✅ Complete            |
| Pull Requests submitted | [MERGED_PRS.md](./MERGED_PRS.md)               | ⏳ Update after merges |
| Reflection              | [REFLECTION.md](./REFLECTION.md)               | ✅ Complete            |
| Evidence Screenshots    | [docs/screenshots](./docs/screenshots)         | ✅ In progress         |

---

## My Repository as a Contribution Target ⭐

SentinelPay received **28 ⭐ stars** and **36 🍴 forks** from classmates in Assignment 14, making it one of the most engaged-with projects in the cohort.

What made SentinelPay fork-friendly:

* Live Swagger UI at `/docs`, so contributors can explore the API without reading every source file first.
* 288 passing tests, giving contributors confidence that changes can be verified quickly.
* `CONTRIBUTING.md` with step-by-step setup instructions from a clean clone.
* `ROADMAP.md` with labelled tasks that classmates could pick up safely.
* MIT License, removing legal barriers to contribution.
* A modular structure that separates models, services, repositories, API routes, and tests.

This helped SentinelPay become more than just my own project. It became a contribution target that other classmates could understand, fork, test, and improve.

* Live Swagger UI at `/docs`, so contributors can explore the API without reading every source file first.
* 288 passing tests, giving contributors confidence that changes can be verified quickly.
* `CONTRIBUTING.md` with step-by-step setup instructions from a clean clone.
* `ROADMAP.md` with labelled tasks that classmates could pick up safely.
* MIT License, removing legal barriers to contribution.
* A modular structure that separates models, services, repositories, API routes, and tests.

This helped SentinelPay become more than just my own project. It became a contribution target that other classmates could understand, fork, test, and improve.

## Contributions Made to Peers' Repositories 🤝

| # | Classmate Repo                                                                                                                          | Issue                                                                                                                                         | PR Link                                                                                                                 | Type                                              | Status      |
| - | --------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- | ----------- |
| 1 | [TailorFit](https://github.com/znxos/TailorFit)                                                                                         | [Issue #40 - API Parameters - 4](https://github.com/znxos/TailorFit/issues/40)                                                                | [PR #1 - Add API key request and response schemas](PASTE_TAILORFIT_PR_LINK_HERE)                                        | `feature-request`, `REST API`, `good-first-issue` | ⏳ Submitted |
| 2 | [ClinicEase Online Doctor Appointment Booking System](https://github.com/222618698/ClinicEase-Online-Doctor-Appointment-Booking-System) | [Issue #13 - Admin generates operational reports](https://github.com/222618698/ClinicEase-Online-Doctor-Appointment-Booking-System/issues/13) | [PR #2 - Document operational reports user story](PASTE_CLINICEASE_PR_LINK_HERE)                                        | `user-story`, `documentation`, `should-have`      | ⏳ Submitted |
| 3 | [Manga Book Store System](https://github.com/Vanessa-Ndomba/manga-book-store-system)                                                    | [Issue #12 - Add OpenAPI JSON + Swagger screenshot to docs/](https://github.com/Vanessa-Ndomba/manga-book-store-system/issues/12)             | [PR #3 - Add OpenAPI JSON and Swagger UI screenshot](https://github.com/Vanessa-Ndomba/manga-book-store-system/pull/22) | `documentation`, `OpenAPI`, `Swagger`             | ⏳ Submitted |

---

## Contribution Stats 📊

| Metric                         |                       Count |
| ------------------------------ | --------------------------: |
| PRs submitted                  |                       3 / 3 |
| PRs merged                     | 0 / 3 - update after merges |
| Repositories contributed to    |                       3 / 3 |
| Feature-request PRs            |                           1 |
| Documentation / user-story PRs |                           2 |
| Local test suites passed       |                           3 |
| TailorFit tests passed         |        32 passed, 1 warning |
| ClinicEase tests passed        |       188 passed, 1 warning |
| Manga Book Store tests passed  |        59 passed, 1 warning |
| Stars received on SentinelPay  |                          28 |
| Forks received on SentinelPay  |                          36 |

| # | Classmate Repo | Issue | PR Link | Type | Status |
|---|---|---|---|---|---|
| 1 | [TailorFit](https://github.com/znxos/TailorFit) | [Issue #40 - API Parameters - 4](https://github.com/znxos/TailorFit/issues/40) | [PR #1 - Add API key request and response schemas](PASTE_TAILORFIT_PR_LINK_HERE) | `feature-request`, `REST API`, `good-first-issue` | ⏳ Submitted |
| 2 | [ClinicEase Online Doctor Appointment Booking System](https://github.com/222618698/ClinicEase-Online-Doctor-Appointment-Booking-System) | [Issue #13 - Admin generates operational reports](https://github.com/222618698/ClinicEase-Online-Doctor-Appointment-Booking-System/issues/13) | [PR #2 - Document operational reports user story](PASTE_CLINICEASE_PR_LINK_HERE) | `user-story`, `documentation`, `should-have` | ⏳ Submitted |
| 3 | [repo link] | [issue link] | [PR link] | `feature-request` | 📝 Planned |

---

## PR #1 - TailorFit API Key Schemas 🔐

For my first contribution, I worked on the **TailorFit** repository. I selected **Issue #40 - API Parameters - 4**, which requested API key request and response schemas.

I added two new Pydantic schemas to `api/schemas.py`:

```text
APIKeyCreate
APIKeyResponse
```

The `APIKeyCreate` schema defines the request body for submitting an API key string. The `APIKeyResponse` schema defines the response body for returning whether the API key is valid and which provider it belongs to.

This was a safe schema-only contribution. I did not change routes, services, repositories, or tests. The purpose was to create a clean foundation for future API-key validation endpoints.

Before submitting the PR, I ran the available checks locally:

```bash
python -m compileall api
pytest
```

Result:
```text
32 passed, 1 warning
```
| Metric | Count |
|---|---:|

| PRs submitted | 2 / 3 |
| PRs merged | 0 / 3 - update after merges |
| Repositories contributed to | 2 / 3 |
| Feature-request PRs | 1 |
| Documentation / user-story PRs | 1 |
| Local test suites passed | 2 |
| TailorFit tests passed | 32 passed, 1 warning |
| ClinicEase tests passed | 188 passed, 1 warning |
| Stars received on SentinelPay | 28 |
| Forks received on SentinelPay | 36 |

---

## PR #2 - ClinicEase Operational Reports Documentation 📊🏥

For my second contribution, I worked on the **ClinicEase Online Doctor Appointment Booking System** repository. I selected **Issue #13 - Admin generates operational reports**.

The issue already included a user story and acceptance criteria, but I noticed that the implementation details could be expanded further. I created a new documentation file:

```text
docs/user-stories/US-013-operational-reports.md
```

This document turns the original user story into a deeper implementation guide. It explains the purpose of operational reports, business value, stakeholder impact, expected report metrics, date range filtering, no-show rate calculation, CSV/PDF export expectations, suggested API behaviour, validation rules, edge cases, suggested test scenarios, and a clear definition of done.

This contribution was intentionally documentation-only. I did not modify services, repositories, API routes, tests, or application logic.

Before submitting the PR, I ran the available checks locally:

```bash
python -m compileall api services repositories src
pytest
```

Result:

```text
188 passed, 1 warning
```

---

## PR #3 - Manga Book Store OpenAPI and Swagger Documentation 📘✨

For my third contribution, I worked on the **Manga Book Store System** repository. I selected **Issue #12 - Add OpenAPI JSON + Swagger screenshot to docs/**.

The issue requested two documentation files inside the `docs/` folder:

```text
docs/openapi.json
docs/swagger-ui.png
```

I generated the OpenAPI JSON directly from the FastAPI application and saved it as `docs/openapi.json`. I also saved a Swagger UI screenshot as `docs/swagger-ui.png`, showing the available Manga, Orders, Users, and root endpoints.

This contribution improves API visibility. Future contributors can now inspect the API contract and Swagger documentation evidence without needing to run the project first.

This was also a documentation-only contribution. I did not modify business logic, routes, services, repositories, schemas, or tests.

Before submitting the PR, I ran the available checks locally:

```bash
python -m compileall api services repositories src
pytest
```

Result:

```text
59 passed, 1 warning
```

---

## Evidence Screenshots Checklist 🖼️

| Screenshot Range | Repository       | Evidence Covered                                                                      |
| ---------------- | ---------------- | ------------------------------------------------------------------------------------- |
| 01 - 08          | TailorFit        | Issue, comment, branch, tests, PR, files changed, CI, merge                           |
| 09 - 17          | ClinicEase       | Issue, comment, branch, tests, PR, files changed, CI, merge                           |
| 18 - 27          | Manga Book Store | Issue, comment, branch, OpenAPI JSON, Swagger UI, tests, PR, files changed, CI, merge |

---

## Key Takeaway 💡

Open-source contribution is 20% code and 80% communication.

A pull request becomes easier to review when it has:

```text
Clear issue link
+ Small focused change
+ Passing tests
+ Good explanation
+ Respect for the existing project
= Maintainer confidence
```

The code itself rarely gets rejected when the scope is clear and the tests pass. What matters most is whether the maintainer can quickly understand what changed, why it was needed, and whether it broke anything.

Assignment 15 helped me practise the real workflow of collaborative development: choosing issues, commenting before coding, creating feature branches, making focused changes, running tests, opening PRs, and tracking evidence professionally.

---

*SentinelPay - Because every millisecond between a transaction and a fraud signal costs money.*
