# Merged Pull Requests — Assignment 15

**Author:** Teboho Mokoni | SentinelPay

---

## Summary

| PR | Repository | Type | Status | 
|---|---|---|---|---|
| [PR #1](#pr-1--tailorfit-api-key-schemas) | [TailorFit](https://github.com/znxos/TailorFit) | `feature-request`, `REST API`, `good-first-issue` | ⏳ Submitted |
| [PR #2](#pr-2) | [classmate-repo-2] | `good-first-issue` | ⏳ Submitted | +10 |
| [PR #3](#pr-3) | [classmate-repo-3] | `feature-request` | ⏳ Submitted | +10 +5 bonus |

> Update the Status column to ✅ Merged once each PR is accepted.
> Add the direct GitHub PR link once submitted.

---

## PR #1

**Repository:** `https://github.com/znxos/TailorFit`  
**PR Link:** `https://github.com/znxos/TailorFit/pull/44`  
**Issue addressed:** `#40 - API Parameters - 4`  
**Branch:** `feature/api-key-schemas`

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

**Repository:** `https://github.com/[classmate-2]/[repo]`  
**PR Link:** `https://github.com/[classmate-2]/[repo]/pull/[number]`  
**Issue addressed:** `#[issue-number] — [issue title]`  
**Branch:** `test/[description]`

### What I changed
_Describe the change — e.g., "Added 5 unit tests for the UserService class
covering the edge cases listed in the issue."_

### Why it was needed
_e.g., "The UserService had 0% test coverage. The issue asked for basic CRUD tests."_

### CI result
_e.g., "CI passed — 5 new tests added, 0 failures."_

---

## PR #3

**Repository:** `https://github.com/[classmate-3]/[repo]`  
**PR Link:** `https://github.com/[classmate-3]/[repo]/pull/[number]`  
**Issue addressed:** `#[issue-number] — [issue title]`  
**Branch:** `feat/[description]`

### What I changed
_Describe the feature — e.g., "Implemented input validation on the POST /api/books
endpoint using Pydantic, returning 422 with a clear error message for invalid fields."_

### Why it was needed
_e.g., "The endpoint accepted any payload without validation, which caused 500 errors
on invalid input instead of a clear 422 response."_

### CI result
_e.g., "CI passed — new validation tests added and passing."_

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
Brief description of what this PR does.

## Related Issue
Closes #[issue-number]

## Changes Made
- [specific change 1]
- [specific change 2]

## Testing
- All existing tests pass
- [any new tests added]

## Screenshots (if applicable)
[paste CI passing screenshot]
```