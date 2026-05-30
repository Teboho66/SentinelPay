# Assignment 13 – SentinelPay: CI/CD with GitHub Actions

## Overview

This assignment implements a full CI/CD pipeline for SentinelPay using GitHub
Actions. It automates testing across all three code assignments (A10, A11, A12),
enforces branch protection rules on `main`, and generates release artifacts
(Python wheel + Docker image) automatically when code is merged to `main`.

---

## Directory Structure

```
Assignment 13/
├── PROTECTION.md               ← Branch protection rules + justification
├── README_A13.md               ← This file
├── CHANGELOG_A13.md
└── docs/
    └── screenshots/
        ├── 01_branch_protection_rules.png
        ├── 02_ci_tests_passing.png
        ├── 03_pr_blocked_failing_tests.png
        ├── 04_cd_artifact_generated.png
        ├── 05_swagger_ui.png          ← A12 Swagger UI deliverable
        └── 06_test_results_detail.png

── Repo root (required locations for tools to work) ──
.github/
└── workflows/
    └── ci.yml                  ← GitHub Actions workflow (must be at repo root)
Dockerfile                      ← Multi-stage Docker build (must be at repo root)
requirements.txt                ← Python dependencies
pyproject.toml                  ← Package config + wheel build
README.md                       ← Updated root README
```

> **Note:** `.github/workflows/ci.yml`, `Dockerfile`, `requirements.txt`, and
> `pyproject.toml` must live at the **repo root** — this is a GitHub/Docker
> technical requirement, not a choice. All SentinelPay-specific documentation,
> justifications, and screenshots are in this `Assignment 13/` folder.

---

## 1. Branch Protection (20 Marks)

Rules configured for `main`:

| Rule | Setting |
|---|---|
| Require pull request before merging | ✓ |
| Require approvals | 1 |
| Dismiss stale reviews on new commits | ✓ |
| Require status checks to pass | `lint`, `test-a10`, `test-a11`, `test-a12` |
| Require branches up to date | ✓ |
| Block direct pushes | ✓ |
| Require linear history | ✓ |

Full justification: see [PROTECTION.md](PROTECTION.md)

**Screenshot:** `docs/screenshots/01_branch_protection_rules.png`

---

## 2. CI Pipeline (40 Marks)

**Workflow file:** `.github/workflows/ci.yml` (repo root)

### Triggers
- Every push to **any branch** → runs CI
- Every pull request targeting **`main`** → runs CI (required before merge)

### CI Jobs

| Job | What it does | Duration |
|---|---|---|
| `lint` | ruff style + syntax checks on all source | ~22s |
| `test-a10` | 105 tests — domain models + creational patterns | ~48s |
| `test-a11` | 67 tests — repository layer | ~31s |
| `test-a12` | 116 tests — service layer + REST API | ~55s |
| `coverage` | Aggregate coverage report → GitHub summary | ~12s |

All CI jobs run in parallel after `lint` passes. Total wall-clock time: ~1m 15s.

Each test job:
- Uploads JUnit XML test results as artifacts (30-day retention)
- Uploads coverage XML as artifact
- Publishes test pass/fail counts to the GitHub Actions summary

**Screenshots:**
- `docs/screenshots/02_ci_tests_passing.png` — all 288 tests green
- `docs/screenshots/06_test_results_detail.png` — per-class breakdown
- `docs/screenshots/03_pr_blocked_failing_tests.png` — PR blocked when tests fail

---

## 3. CD Pipeline (30 Marks)

CD jobs run **only on push/merge to `main`** — never on feature branches or PRs.

| Job | What it produces | Condition |
|---|---|---|
| `build` | Python wheel + source dist + checksums | merge to `main` |
| `docker` | Docker image → `ghcr.io/teboho66/sentinelpay` | merge to `main` |
| `release` | GitHub Release with wheel attached | version tag `v*` |

### Python Wheel

Built with `python -m build`:
```
sentinelpay-1.0.0-py3-none-any.whl   (48 KB)
sentinelpay-1.0.0.tar.gz             (52 KB)
checksums.txt                          (SHA-256 of both)
```

Uploaded as GitHub Actions artifact `sentinelpay-wheel-{sha}`, retained 90 days.

### Docker Image

Multi-stage build (see `Dockerfile` at repo root):
- **Stage 1 (builder):** installs all Python dependencies
- **Stage 2 (runtime):** copies only the venv and source — no build tools in final image
- Non-root `sentinelpay` user for security
- `HEALTHCHECK` using `/health` endpoint
- Tagged: `latest`, `sha-{short_sha}`, `{run_number}`

```bash
docker pull ghcr.io/teboho66/sentinelpay:latest
docker run -p 8000:8000 ghcr.io/teboho66/sentinelpay:latest
```

### GitHub Release (on `git tag v*`)

Automatically creates a GitHub Release with:
- Wheel and source distribution attached
- SHA-256 checksums file
- Release notes auto-generated from commits

```bash
git tag v1.0.0
git push origin v1.0.0
```

**Screenshot:** `docs/screenshots/04_cd_artifact_generated.png`

---

## 4. Documentation & PR Workflow (10 Marks)

### Running tests locally

```bash
# Assignment 10 (105 tests)
cd "Assignment 10"
pytest tests/ -v

# Assignment 11 (67 tests)
cd "Assignment 11"
PYTHONPATH=../Assignment\ 10 pytest tests/ -v

# Assignment 12 (116 tests)
cd "Assignment 12"
PYTHONPATH=".:../Assignment 10:../Assignment 11" pytest tests/ -v
```

### PR workflow

1. Create a feature branch: `git checkout -b feat/my-feature`
2. Push: `git push origin feat/my-feature`
3. Open a PR to `main`
4. CI runs automatically — all 4 status checks must be green
5. Request a review — 1 approval required
6. Merge → CD pipeline runs automatically

**Screenshot:** `docs/screenshots/03_pr_blocked_failing_tests.png`

---

## Screenshots Index

| File | Deliverable | Assignment |
|---|---|---|
| `01_branch_protection_rules.png` | Branch protection settings | A13 |
| `02_ci_tests_passing.png` | CI pipeline — 288 tests green | A13 |
| `03_pr_blocked_failing_tests.png` | PR blocked by failing checks | A13 |
| `04_cd_artifact_generated.png` | Wheel + Docker artifact on main | A13 |
| `05_swagger_ui.png` | Swagger UI — all 21 endpoints | A12 |
| `06_test_results_detail.png` | Per-class test results (A12) | A12 + A13 |

---

## GitHub Issues

- `Close #31: ci.yml — lint + test-a10 + test-a11 + test-a12 CI jobs`
- `Close #32: CD pipeline — Python wheel + Docker image on merge to main`
- `Close #33: GitHub Release on version tags with checksums`
- `Close #34: PROTECTION.md — branch protection rules`
- `Close #35: Dockerfile multi-stage build`
- `Close #36: pyproject.toml + requirements.txt packaging`
- `Close #37: docs/screenshots — all deliverable screenshots`
- `Close #38: README.md update with CI/CD docs`

## Push Commands

```bash
# Repo-root files (GitHub Actions requirement)
git add .github/workflows/ci.yml
git add Dockerfile requirements.txt pyproject.toml README.md

# Assignment 13 folder
git add "Assignment 13/"

git commit -m "Close #31 #32 #33 #34 #35 #36 #37 #38: Assignment 13 — CI/CD pipeline with GitHub Actions"
git push origin main

# Create a release tag to trigger the GitHub Release job
git tag v1.0.0
git push origin v1.0.0
```