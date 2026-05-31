# Contributing to SentinelPay

Thank you for your interest in contributing to SentinelPay!
This guide will get you from zero to a merged pull request.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [Running the API](#running-the-api)
- [Running Tests](#running-tests)
- [Coding Standards](#coding-standards)
- [How to Pick an Issue](#how-to-pick-an-issue)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Code of Conduct](#code-of-conduct)

---

## Prerequisites

| Tool | Minimum version | How to check |
|---|---|---|
| Python | 3.12 | `python --version` |
| Git | 2.40 | `git --version` |
| Docker (optional) | 24.0 | `docker --version` |

---

## Local Setup

```bash
# 1. Fork the repository on GitHub (click the Fork button)

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/SentinelPay.git
cd SentinelPay

# 3. Create a virtual environment
python -m venv .venv
source .venv/bin/activate          # Linux/Mac
.venv\Scripts\activate             # Windows

# 4. Install dependencies
pip install -r requirements.txt
```

---

## Running the API

```bash
cd "Assignment 12"
python run.py
```

Visit http://localhost:8000/docs for the Swagger UI.

---

## Running Tests

Run all 288 tests before opening a PR:

```bash
# Assignment 10 — Domain models + creational patterns (105 tests)
cd "Assignment 10"
pytest tests/ -v

# Assignment 11 — Repository layer (67 tests)
cd "Assignment 11"
PYTHONPATH="../Assignment 10" pytest tests/ -v

# Assignment 12 — Service layer + REST API (116 tests)
cd "Assignment 12"
PYTHONPATH=".:../Assignment 10:../Assignment 11" pytest tests/ -v
```

**All tests must pass before you open a PR.** The CI pipeline will run them
automatically and block your PR if any fail.

---

## Coding Standards

We use **ruff** for linting:

```bash
pip install ruff
ruff check "Assignment 12/services/" "Assignment 12/api/"
```

Rules:
- No unused imports (`F401`)
- No undefined names (`F821`)
- PEP 8 style (`E` codes)
- Line length is not enforced (E501 ignored) — write readable code

**Every new feature must have tests.** We target ≥ 80% coverage on new code.

---

## How to Pick an Issue

1. Go to the [Issues tab](https://github.com/Teboho66/SentinelPay/issues)
2. Filter by label:
   - **`good-first-issue`** — great starting points, well-scoped
   - **`feature-request`** — larger improvements, discuss first
   - **`bug`** — something broken that needs fixing
3. Comment on the issue: *"I'd like to work on this"* — this reserves it
4. If no one has claimed it within 7 days, it's yours

---

## Submitting a Pull Request

```bash
# 1. Create a feature branch (never commit directly to main)
git checkout -b feat/your-feature-name

# 2. Make your changes
# 3. Run the tests — all must pass
# 4. Commit with a descriptive message
git commit -m "feat: add Redis caching for AccountProfile velocity counters"

# 5. Push
git push origin feat/your-feature-name

# 6. Open a PR on GitHub
#    - Base: main
#    - Title: clear one-liner describing the change
#    - Body: what changed, why, how to test it
#    - Link the issue: "Closes #42"
```

### PR Checklist

Before marking your PR as ready for review:

- [ ] All existing tests still pass
- [ ] New tests written for new code
- [ ] `ruff check` passes with no errors
- [ ] PR description explains the change clearly
- [ ] Issue number linked in the PR body

---

## Code of Conduct

- Be respectful and constructive in reviews
- Explain *why*, not just *what* when requesting changes
- Assume good intent

---

*SentinelPay — Author: Teboho Mokoni | CPUT Postgraduate Diploma*
