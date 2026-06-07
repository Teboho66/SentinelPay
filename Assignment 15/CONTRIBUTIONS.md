# CONTRIBUTIONS.md - Assignment 15 Submission 🌍

**Author:** Teboho Mokoni
**Repository:** https://github.com/Teboho66/SentinelPay
**Assignment:** 15 - Cross-Project Contributions & Collaborative Development

---

## Quick Links

| Deliverable             | File                                           | Status                     |
| ----------------------- | ---------------------------------------------- | -------------------------- |
| Contribution Plan       | [CONTRIBUTION_PLAN.md](./CONTRIBUTION_PLAN.md) | ✅ Complete                 |
| Pull Requests submitted | [MERGED_PRS.md](./MERGED_PRS.md)               | ✅ Updated - 5 merged       |
| Reflection              | [REFLECTION.md](./REFLECTION.md)               | ✅ Complete                 |
| Evidence Screenshots    | [docs/screenshots](./docs/screenshots)         | ✅ Updated with PR evidence |

---

## My Repository as a Contribution Target ⭐

SentinelPay received **28 ⭐ stars** and **37 🍴 forks** from classmates in Assignment 14, making it one of the most engaged-with projects in the cohort.

What made SentinelPay fork-friendly:

* Live Swagger UI at `/docs`, so contributors can explore the API without reading every source file first.
* 288 passing tests, giving contributors confidence that changes can be verified quickly.
* `CONTRIBUTING.md` with step-by-step setup instructions from a clean clone.
* `ROADMAP.md` with labelled tasks that classmates could pick up safely.
* MIT License, removing legal barriers to contribution.
* A modular structure that separates models, services, repositories, API routes, and tests.

This helped SentinelPay become more than just my own project. It became a contribution target that other classmates could understand, fork, test, and improve.

---

## Contributions Made to Peers' Repositories 🤝

| # | Classmate Repo                                                                                                                          | Issue                                                                                                                                            | PR Link                                                                                                                                      | Type                                                    | Status   |
| - | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- | -------- |
| 1 | [TailorFit](https://github.com/znxos/TailorFit)                                                                                         | [Issue #40 - API Parameters - 4](https://github.com/znxos/TailorFit/issues/40)                                                                   | [PR #44 - Add API key request and response schemas](https://github.com/znxos/TailorFit/pull/44)                                              | `feature-request`, `REST API`, `good-first-issue`       | ✅ Merged |
| 2 | [ClinicEase Online Doctor Appointment Booking System](https://github.com/222618698/ClinicEase-Online-Doctor-Appointment-Booking-System) | [Issue #13 - Admin generates operational reports](https://github.com/222618698/ClinicEase-Online-Doctor-Appointment-Booking-System/issues/13)    | [PR #20 - Document operational reports user story](https://github.com/222618698/ClinicEase-Online-Doctor-Appointment-Booking-System/pull/20) | `user-story`, `documentation`, `should-have`            | ✅ Merged |
| 3 | [Manga Book Store System](https://github.com/Vanessa-Ndomba/manga-book-store-system)                                                    | [Issue #12 - Add OpenAPI JSON + Swagger screenshot to docs/](https://github.com/Vanessa-Ndomba/manga-book-store-system/issues/12)                | [PR #22 - Add OpenAPI JSON and Swagger UI screenshot](https://github.com/Vanessa-Ndomba/manga-book-store-system/pull/22)                     | `documentation`, `OpenAPI`, `Swagger`                   | ✅ Merged |
| 4 | [Carwash Booking Queue System](https://github.com/ongeziwe17/carwash-booking-queue-system)                                              | [Issue #76 - Improve validation error responses with field-level messages](https://github.com/ongeziwe17/carwash-booking-queue-system/issues/76) | [PR #78 - Improve validation error responses with field-level messages](https://github.com/ongeziwe17/carwash-booking-queue-system/pull/78)  | `validation`, `REST API`, `testing`, `backend`          | ✅ Merged |
| 5 | [CampusFind1](https://github.com/MissDidiza/campusfind1)                                                                                | [Issue #1 - Add pagination to list endpoints](https://github.com/MissDidiza/campusfind1/issues/1)                                                | [PR #PUT_NUMBER_HERE - Add pagination to list endpoints](https://github.com/MissDidiza/campusfind1/pull/11)                                                      | `good-first-issue`, `REST API`, `pagination`, `testing` | ✅ Merged |

---

## Contribution Stats 📊

| Metric                             |                          Count |
| ---------------------------------- | -----------------------------: |
| PRs submitted                      |                          5 / 5 |
| PRs merged                         |                          5 / 5 |
| Repositories contributed to        |                          5 / 5 |
| Feature-request PRs                |                              1 |
| Documentation / user-story PRs     |                              2 |
| API / backend improvement PRs      |                              2 |
| Local test suites passed           |                              5 |
| TailorFit tests passed             |           32 passed, 1 warning |
| ClinicEase tests passed            |          188 passed, 1 warning |
| Manga Book Store tests passed      |           59 passed, 1 warning |
| Carwash Booking Queue tests passed | 58 tests passed, BUILD SUCCESS |
| CampusFind1 tests passed           |       123 passed, 443 warnings |
| Stars received on SentinelPay      |                             28 |
| Forks received on SentinelPay      |                             37 |

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

## PR #4 - Carwash Field-Level Validation Error Responses 🚗🧼

For my fourth contribution, I worked on the **Carwash Booking Queue System** repository. I selected **Issue #76 - Contr-005: Improve validation error responses with field-level messages**.

This was a backend API quality improvement in a Spring Boot project. The issue explained that validation errors were being grouped together with other bad-request exceptions. Because of that, API consumers received less readable error messages that did not clearly identify which request fields were invalid.

I improved this by adding a dedicated `MethodArgumentNotValidException` handler in the global API exception handler. The new handler builds a clearer validation message that includes field names and readable validation reasons.

I also updated booking request validation by adding validation annotations to `CreateBookingRequest`, including:

```text
@NotBlank
@NotNull
@Future
```

Then I enabled request validation in `BookingController` by adding `@Valid` to the booking create and update request bodies.

Finally, I added an integration test to confirm that an invalid booking request returns HTTP 400 and includes field-level validation details in the response body.

This contribution was more technical than my earlier documentation contributions because it required understanding the Spring Boot exception handling flow, request DTO validation, controller validation activation, and integration testing with MockMvc.

Before submitting the PR, I ran the full Maven test suite locally:

```bash
./mvnw test
```

Result:

```text
Tests run: 58, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

A setup issue occurred at first because the Codespace was using Java 11 while the project requires Java 21. After installing and switching to Java 21, the full test suite passed successfully.

---

## PR #5 - CampusFind1 Pagination for List Endpoints 📄

For my fifth contribution, I worked on the **CampusFind1** repository. I selected **Issue #1 - Add pagination to list endpoints**, which was labelled as a good first issue.

The existing FastAPI list endpoints returned full result sets. I improved the API by adding pagination support through `page` and `limit` query parameters.

I updated list endpoints for:

```text
Users
Reports
Matches
```

The change allows API clients to request smaller result sets instead of always receiving every record. This improves API usability and prepares the project for larger datasets.

This was a focused backend contribution. I did not change service logic, repository logic, domain models, or unrelated files.

I also added API tests to verify:

```text
Paginated users endpoint
Paginated reports endpoint
Invalid pagination values
```

Before submitting the PR, I installed the local test dependencies manually because the repository did not include a requirements file:

```bash
pip install fastapi uvicorn httpx pytest pydantic
python -m compileall api services repositories src
pytest
```

Result:

```text
123 passed, 443 warnings
```

The warnings were existing deprecation warnings and were unrelated to my pagination change.

---

## Evidence Screenshots Checklist 🖼️

| Screenshot Range | Repository                   | Evidence Covered                                                                      |
| ---------------- | ---------------------------- | ------------------------------------------------------------------------------------- |
| 01 - 08          | TailorFit                    | Issue, comment, branch, tests, PR, files changed, CI, merge                           |
| 09 - 17          | ClinicEase                   | Issue, comment, branch, tests, PR, files changed, CI, merge                           |
| 18 - 27          | Manga Book Store             | Issue, comment, branch, OpenAPI JSON, Swagger UI, tests, PR, files changed, CI, merge |
| 28 - 37          | Carwash Booking Queue System | Issue, comment, branch, Java setup, code changes, tests, PR, files changed, CI, merge |
| 38 - 46          | CampusFind1                  | Issue, comment, branch, pagination changes, tests, PR, files changed, CI, merge       |

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
