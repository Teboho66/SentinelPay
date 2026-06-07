# Contribution Plan - Assignment 15

**Author:** Teboho Mokoni | SentinelPay  
**Assignment:** 15 - Cross-Project Contributions & Collaborative Development

---

## Strategy Overview 🚀

My approach for Assignment 15 was to contribute to classmates' repositories using a realistic open-source workflow.

I focused on small, safe, reviewable pull requests that would not break existing systems. I started with schema and documentation contributions because they are valuable, low-risk, and easier for maintainers to review. This allowed me to demonstrate collaboration, communication, testing discipline, and respect for each project’s existing structure.

Before working on each issue, I commented on the GitHub issue first. This showed professional etiquette and helped avoid duplicate work. After that, I created a separate branch, made a focused change, ran local checks, committed clearly, pushed the branch, and opened a pull request linked to the issue.

---

## Projects Selected for Contribution

### Project 1 - TailorFit

**Repo:** `https://github.com/znxos/TailorFit`  
**Issue:** `#40 - API Parameters - 4`  
**Branch:** `feature/api-key-schemas`  
**Contribution Type:** `feature-request`, `REST API`, `good-first-issue`

| Issue | Type | My approach |
|---|---|---|
| API Parameters - 4 | `feature-request`, `REST API` | Add API key request and response schemas using Pydantic |

I selected TailorFit because the issue was clear and aligned with my experience using FastAPI and Pydantic schemas. I kept the contribution small by adding only the requested schema models without changing routes, services, or repository logic.

---

### Project 2 - ClinicEase Online Doctor Appointment Booking System

**Repo:** `https://github.com/222618698/ClinicEase-Online-Doctor-Appointment-Booking-System`  
**Issue:** `#13 - Admin generates operational reports`  
**Branch:** `docs/us-013-operational-reports`  
**Contribution Type:** `user-story`, `documentation`, `should-have`

| Issue | Type | My approach |
|---|---|---|
| Admin generates operational reports | `user-story`, `documentation` | Expand the user story into a detailed implementation guide |

I selected ClinicEase because the issue had a meaningful healthcare administration use case. Instead of implementing a large reporting feature, I made a focused documentation contribution that clarified the business value, expected metrics, validation rules, edge cases, API behaviour, test scenarios, and definition of done.

---

### Project 3 - Manga Book Store System

**Repo:** `https://github.com/Vanessa-Ndomba/manga-book-store-system`  
**Issue:** `#12 - Add OpenAPI JSON + Swagger screenshot to docs/`  
**Branch:** `docs/openapi-swagger-evidence`  
**Contribution Type:** `documentation`, `OpenAPI`, `Swagger`

| Issue | Type | My approach |
|---|---|---|
| Add OpenAPI JSON + Swagger screenshot to docs/ | `documentation`, `OpenAPI`, `Swagger` | Add the generated OpenAPI JSON file and Swagger UI screenshot to the docs folder |

I selected Manga Book Store because the issue was clear, scoped, and documentation-focused. I generated the OpenAPI JSON from the FastAPI app and saved a Swagger UI screenshot using the exact filenames requested by the issue.

---

### Project 4 - Carwash Booking Queue System

**Repo:** `https://github.com/ongeziwe17/carwash-booking-queue-system`  
**Issue:** `#76 - Improve validation error responses with field-level messages`  
**Branch:** `feature/field-level-validation-errors`  
**Contribution Type:** `validation`, `REST API`, `testing`, `backend`

| Issue | Type | My approach |
|---|---|---|
| Improve validation error responses with field-level messages | `validation`, `REST API`, `testing`, `backend` | Add field-level validation error responses and integration tests |

I selected the Carwash Booking Queue System because this issue was more technical than my earlier documentation-focused contributions. It required backend API work in a Spring Boot project, specifically around validation error handling.

The original problem was that `MethodArgumentNotValidException` was grouped together with other bad-request exceptions. This meant validation failures returned less readable messages using `ex.getMessage()`. My approach was to separate validation failures into a dedicated handler, return clearer field-level messages, apply validation annotations to booking requests, and add an integration test that confirms the response body contains invalid field names.

This contribution strengthened my Assignment 15 portfolio because it shows I can contribute beyond documentation by improving API usability, validation behaviour, and test coverage in a Java/Spring Boot codebase.

---

### Project 5 - CampusFind1

**Repo:** `https://github.com/MissDidiza/campusfind1`  
**Issue:** `#1 - Add pagination to list endpoints`  
**Branch:** `feature/add-pagination-list-endpoints`  
**Contribution Type:** `good-first-issue`, `REST API`, `pagination`, `testing`

| Issue | Type | My approach |
|---|---|---|
| Add pagination to list endpoints | `good-first-issue`, `REST API`, `pagination`, `testing` | Add `page` and `limit` query parameters to list endpoints and verify the behaviour with API tests |

I selected CampusFind1 because the issue was clearly labelled as a good first issue and focused on improving API usability. The project already had FastAPI list endpoints for users, reports, and matches, but they returned full result sets without pagination.

My approach was to keep the contribution focused by adding `page` and `limit` query parameters to the existing list endpoints without changing service logic, repository logic, domain models, or unrelated files. I also added API tests to verify paginated user and report responses, as well as validation for invalid pagination values.

This contribution strengthened my Assignment 15 portfolio because it shows another backend API improvement with testing, while still following a small and reviewable pull request style.

---

## Contribution Priority

1. **Communication first**  
   I commented on each issue before starting work to show intent and avoid duplicate contributions.

2. **Small changes second**  
   I kept each pull request focused on one task only. This made the PRs easier to review.

3. **Testing third**  
   I ran the available local checks before opening each PR, even for documentation-only changes.

4. **Evidence last**  
   I captured screenshots of issues, comments, tests, PRs, files changed, and CI/merge status for Assignment 15 reporting.

---

## PR Quality Checklist

* [x] Read or inspected the project structure before editing
* [x] Commented on the issue before working
* [x] Created a branch with a descriptive name
* [x] Made one focused change per PR
* [x] Avoided unrelated files
* [x] Avoided committing `.venv`, `__pycache__`, or build artifacts
* [x] Ran local tests or compile checks
* [x] Wrote clear commit messages
* [x] Linked each PR to its issue
* [x] Explained what changed and why in the PR body
* [x] Captured screenshots for evidence

---

## Final Contribution Plan Outcome

| PR | Repository | Focus | Local Result | Final Status |
|---|---|---|---|---|
| PR #1 | TailorFit | API key schemas | 32 passed, 1 warning | ✅ Merged |
| PR #2 | ClinicEase | Operational reports documentation | 188 passed, 1 warning | ✅ Merged |
| PR #3 | Manga Book Store | OpenAPI JSON and Swagger screenshot | 59 passed, 1 warning | ✅ Merged |
| PR #4 | Carwash Booking Queue System | Field-level validation error responses | 58 tests passed, BUILD SUCCESS | ✅ Merged |
| PR #5 | CampusFind1 | Pagination for list endpoints | 123 passed, 443 warnings | ✅ Merged |

This plan helped me complete five cross-project contributions while keeping each change professional, safe, and easy for maintainers to review. All five peer contributions were submitted and merged successfully.