# Merged Pull Requests — Assignment 15

**Author:** Teboho Mokoni | SentinelPay

---

## Summary

| PR | Repository | Type | Status |
|---|---|---|---|
| [PR #1](#pr-1--tailorfit-api-key-schemas) | [TailorFit](https://github.com/znxos/TailorFit) | `feature-request`, `REST API`, `good-first-issue` | ✅ Merged |
| [PR #2](#pr-2--clinicease-operational-reports-documentation) | [ClinicEase Online Doctor Appointment Booking System](https://github.com/222618698/ClinicEase-Online-Doctor-Appointment-Booking-System) | `user-story`, `documentation`, `should-have` | ⏳ Submitted |
| [PR #3](#pr-3--manga-book-store-openapi-and-swagger-documentation) | [Manga Book Store System](https://github.com/Vanessa-Ndomba/manga-book-store-system) | `documentation`, `OpenAPI`, `Swagger` | ✅ Merged |
| [PR #4](#pr-4--carwash-field-level-validation-error-responses) | [Carwash Booking Queue System](https://github.com/ongeziwe17/carwash-booking-queue-system) | `validation`, `REST API`, `testing`, `backend` | ⏳ Submitted |


> Update the Status column to ✅ Merged once each PR is accepted.
> Add the direct GitHub PR link once submitted.

---

## PR #1

**Repository:** `https://github.com/znxos/TailorFit`  
**PR Link:** `https://github.com/znxos/TailorFit/pull/44`  
**Issue addressed:** `#40 - API Parameters - 4`  
**Branch:** `feature/api-key-schemas`
**Status:** ✅ Merged  

### What I changed

Added two new Pydantic schemas to `api/schemas.py` for API key validation support:

- `APIKeyCreate`
  - Defines the request body for submitting an API key.
  - Adds validation for `key_string` with `min_length=1` and `max_length=256`.

- `APIKeyResponse`
  - Defines the response body for API key validation results.
  - Includes `is_valid` to indicate whether the key passed validation.
  - Includes `provider`, defaulting to `"Unknown"`.

This is a schema-only change. It does not modify existing routes, services, repositories, or test logic.

### Why it was needed

Closes #40

Issue #40 requested API key request and response schemas so the project can support future API key validation or authentication endpoints.

Previously, the project did not have a dedicated request model for receiving an API key string or a response model for returning whether the key is valid. Adding these schemas provides a clean, typed foundation for future API-key-related endpoints while keeping the current application behavior unchanged.

### CI result

All existing tests pass locally.

Commands run:

```bash
python -m compileall api
pytest
---

## PR #2

**Repository:** `https://github.com/222618698/ClinicEase-Online-Doctor-Appointment-Booking-System`  
**PR Link:** `https://github.com/222618698/ClinicEase-Online-Doctor-Appointment-Booking-System/pull/20`  
**Issue addressed:** `[#13] - [[US-013] Admin generates operational reports]`  
**Issue addressed:** `#13 - [US-013] Admin generates operational reports`  
**Branch:** `test/[description]`

### What I changed
I added a detailed documentation file for **US-013: Admin generates operational reports**.

The new file is located at:

```text
docs/user-stories/US-013-operational-reports.md

### Why it was needed
The issue already had a user story and acceptance criteria, but the implementation details needed more depth so future contributors could build the feature with less confusion.

Operational reports are important because clinic administrators need a reliable way to monitor clinic performance. The documentation now explains how reports should calculate appointment totals, no-show rates, appointments per doctor, and no-data scenarios. It also explains how the feature could later support CSV and PDF downloads.

This makes the user story more complete, easier to implement, easier to test, and easier for the maintainer to review in future development work.

### CI result
CI result

All existing checks passed locally.

Commands run:

python -m compileall api services repositories src
pytest

Result:
188 passed, 1 warning

The single warning was an existing Starlette/FastAPI test client deprecation warning and was unrelated to my documentation-only change.

---

## PR #3 - Manga Book Store OpenAPI and Swagger Documentation 📘✨

**Repository:** `https://github.com/Vanessa-Ndomba/manga-book-store-system`
**PR Link:** `https://github.com/Vanessa-Ndomba/manga-book-store-system/pull/22`
**Issue addressed:** `#12 - Add OpenAPI JSON + Swagger screenshot to docs/`
**Branch:** `docs/openapi-swagger-evidence`

### What I changed

For my third cross-project contribution, I worked on the **Manga Book Store System** repository. I selected **Issue #12**, which requested that the project’s OpenAPI JSON file and Swagger UI screenshot be saved inside the `docs/` folder.

I added the following two files:

```text
docs/openapi.json
docs/swagger-ui.png
```

The `openapi.json` file was generated directly from the FastAPI application. This file captures the current API specification, including the available Manga, Orders, Users, and root endpoints.

The `swagger-ui.png` file provides a visual screenshot of the Swagger UI page. It shows the API documentation interface and makes it easier for contributors to quickly understand the available routes without needing to run the project first.

This was a documentation-focused contribution. I did not change any business logic, services, repositories, schemas, routes, or tests.

### Why it was needed

The issue requested API documentation evidence to be committed inside the `docs/` folder. Before this contribution, the repository had some screenshots, but the issue specifically asked for clearly named documentation files:

```text
docs/openapi.json
docs/swagger-ui.png
```

Adding these files improves the project because API documentation is one of the first things future contributors look for when trying to understand a backend system. The OpenAPI JSON provides a machine-readable API contract, while the Swagger screenshot provides a human-readable visual reference.

This makes the project more contributor-friendly and helps future developers understand the current backend structure more quickly.

### CI result

I ran the available checks locally before submitting the pull request.

Commands run:

```bash
python -m compileall api services repositories src
pytest
```

Result:

```text
59 passed, 1 warning
```

The single warning was an existing Starlette/FastAPI test client deprecation warning and was unrelated to my documentation-only change.

---

## How to submit a PR to a classmate's repo

```bash
# 1. Fork their repo on GitHub (click Fork button)

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/their-repo.git
cd their-repo

# 3. Create a branch
git checkout -b fix/your-description

# 4. Make your change, then commit
git add .
git commit -m "fix: resolve missing import in conftest.py (Closes #12)"

# 5. Push to your fork
git push origin fix/your-description

# 6. Open a PR on GitHub
# Go to their repo → Pull requests → New pull request
# Set base: main, compare: your-fork/fix/your-description
```

### PR description template to copy-paste

```
## Summary

Added the requested API documentation evidence to the `docs/` folder.

This PR adds:

* `docs/openapi.json`
* `docs/swagger-ui.png`

The OpenAPI JSON was generated from the FastAPI application, and the Swagger UI screenshot shows the current MangaBookStore API documentation page with the available Manga, Orders, Users, and root endpoints.

## Related Issue

Closes #12

## Changes Made

* Added `docs/openapi.json` containing the generated FastAPI OpenAPI specification.
* Added `docs/swagger-ui.png` showing the Swagger UI page for the current API.
* Kept the contribution documentation-only with no changes to business logic, routes, services, repositories, schemas, or tests.

## Testing

All available checks pass locally.

Commands run:

```bash
python -m compileall api services repositories src
pytest
```

Result:

```text
59 passed, 1 warning
```

The warning is an existing Starlette/FastAPI test client deprecation warning and is unrelated to this documentation-only change.

## Screenshots

Swagger UI screenshot added in:

```text
docs/swagger-ui.png
```

```