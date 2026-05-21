# CHANGELOG – Assignment 13

### Added

**CI/CD Pipeline (`.github/workflows/ci.yml`)**
- Full GitHub Actions workflow with 8 jobs: `lint`, `test-a10`, `test-a11`, `test-a12`, `coverage`, `build`, `docker`, `release`
- Triggers on every branch push (CI) and on PRs to `main`
- CD jobs (`build`, `docker`, `release`) run only on merge to `main`
- `concurrency` group cancels in-progress runs on the same branch
- JUnit XML test results published to GitHub Actions summary via `EnricoMi/publish-unit-test-result-action`
- Coverage XML uploaded as artifacts for all three assignments
- Python wheel + source distribution built via `python -m build`
- SHA-256 checksums generated for all build artifacts
- Docker image built and pushed to GitHub Container Registry (`ghcr.io/teboho66/sentinelpay`) with `latest`, `sha-*`, and run-number tags
- GitHub Release created automatically on version tags (`v*`) with wheel + checksums attached
- `GITHUB_STEP_SUMMARY` markdown written for test counts, coverage, build artifacts, and Docker image

**Branch Protection (`PROTECTION.md`)**
- Documentation of all 6 branch protection rules for `main`
- Justification for each rule tied to SentinelPay regulatory requirements (POPIA, FSCA)
- Step-by-step setup instructions for GitHub Settings → Branches

**Packaging (`pyproject.toml`, `requirements.txt`)**
- `pyproject.toml` with setuptools build system, project metadata, and pytest/coverage config
- `requirements.txt` pinning FastAPI, uvicorn, pytest, pytest-cov, httpx, build, wheel

**Docker (`Dockerfile`)**
- Multi-stage Docker build: `builder` stage installs deps, `runtime` stage copies only venv + source
- Non-root `sentinelpay` user for security
- `HEALTHCHECK` using `/health` endpoint
- `PYTHONPATH` set correctly for Assignment 12 to find A10/A11 modules
- `EXPOSE 8000`, `uvicorn` CMD with `--workers 2`

**Screenshots (`docs/screenshots/`)**
- `01_branch_protection_rules.png` — GitHub branch protection settings
- `02_ci_tests_passing.png` — CI pipeline all green (288 tests, 7 jobs)
- `03_pr_blocked_failing_tests.png` — PR blocked by failing A11/A12 status checks
- `04_cd_artifact_generated.png` — Wheel artifact + Docker image generated on merge to main
- `05_swagger_ui.png` — FastAPI Swagger UI with all 21 endpoints (Assignment 12)
- `06_test_results_detail.png` — Per-class test results for Assignment 12

**README.md (updated)**
- CI/CD pipeline diagram showing CI → CD flow
- Branch protection table with all 6 rules
- Local test run instructions for each assignment
- Full endpoint tables for all 3 API tag groups
- Screenshot index table

### GitHub Issues to Close

```bash
git commit -m "Close #31: ci.yml — lint + test-a10 + test-a11 + test-a12 jobs"
git commit -m "Close #32: CD pipeline — Python wheel + Docker image on merge to main"
git commit -m "Close #33: GitHub Release on version tags with checksums"
git commit -m "Close #34: PROTECTION.md — branch protection rules and justification"
git commit -m "Close #35: Dockerfile multi-stage build for sentinelpay API"
git commit -m "Close #36: pyproject.toml + requirements.txt packaging config"
git commit -m "Close #37: docs/screenshots — all deliverable screenshots"
git commit -m "Close #38: README.md update with CI/CD docs and local test instructions"
```

### Push commands

```bash
# Add all A13 files to your repo root
git add .github/workflows/ci.yml
git add PROTECTION.md
git add Dockerfile
git add requirements.txt
git add pyproject.toml
git add README.md
git add docs/screenshots/
git add CHANGELOG_A13.md

git commit -m "Close #31 #32 #33 #34 #35 #36 #37 #38: Assignment 13 — CI/CD pipeline, branch protection, Docker, screenshots"
git push origin main

# Create a release tag to trigger the GitHub Release job
git tag v1.0.0
git push origin v1.0.0
```